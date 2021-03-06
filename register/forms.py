from django import forms
from django.conf import settings
from nextcloud import NextCloud

from register.models import InviteCode


class RegisterForm(forms.Form):
    invite_code = forms.UUIDField()
    username = forms.CharField(max_length=191)
    password = forms.CharField(widget=forms.PasswordInput())
    display_name = forms.CharField(max_length=191)

    def clean_invite_code(self):
        code = self.cleaned_data['invite_code']
        try:
            invite_code = InviteCode.objects.get(code=code, used=False)
        except InviteCode.DoesNotExist:
            raise forms.ValidationError("Invite code invalid or already used.", code="invalid")
        return code

    def dummy_create_account(self):
        print("LOL THIS WOULD DO SOMETHING!")
        # Invalidate invite code
        code = InviteCode.objects.get(code=self.cleaned_data['invite_code'])
        code.used = True
        code.used_by = self.cleaned_data['username']
        code.save()
        return True, ""

    def create_account(self):
        nc = NextCloud(endpoint=settings.NEXTCLOUD_URL, user=settings.NEXTCLOUD_USER, password=settings.NEXTCLOUD_PASSWORD, json_output=True)
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        display_name = self.cleaned_data['display_name']

        new_user_res = nc.add_user(username, password)
        if new_user_res.status_code != 100:
            try:
                msg = {
                    101: "invalid input data",
                    102: "username already exists",
                    103: "unknown error occurred whilst adding the user",
                    104: "group does not exist",
                    105: "insufficient privileges for group",
                    106: "no group specified (required for subadmins)",
                    107: "all errors that contain a hint - for example “Password is among the 1,000,000 most common ones. Please make it unique.” (this code was added in 12.0.6 & 13.0.1)",
                    108: "password and email empty. Must set password or an email",
                    109: "invitation email cannot be send",
                }[new_user_res.status_code]
                if new_user_res.status_code == 107:
                    msg = new_user_res.full_data['ocs']['meta']['message']
            except KeyError:
                msg = "An unknown error occurred. Please try again later"
            return False, msg

        # Invalidate invite code
        code = InviteCode.objects.get(code=self.cleaned_data['invite_code'])
        code.used = True
        code.used_by = username
        code.save()

        # Set user parameters and add to wanted group
        edit_display_res = nc.edit_user(username, 'displayname', display_name)
        if code.groups:
            groups = code.groups.split(",")
            results = []
            for group in groups:
                add_viewers_res = nc.add_to_group(username, group)
                results.append((group, add_viewers_res))
        else:
            add_viewers_res = nc.add_to_group(username, settings.NEXTCLOUD_GROUP_NAME)
            results = [(settings.NEXTCLOUD_GROUP_NAME, add_viewers_res)]

        if edit_display_res.status_code == 100 and all([x[1].status_code == 100 for x in results]):
            return True, ""

        reasons = []
        if edit_display_res.status_code == 101:
            reasons.append("Could not update display name, user not found.")
        elif edit_display_res.status_code == 102:
            reasons.append("Could not update display name, invalid display name.")
        else:
            reasons.append("Could not update display name, unknown error.")

        for group, result in results:
            if result.status_code == 101:
                reasons.append("Could not add user to group '{}', group not specified.".format(group))
            elif result.status_code == 102:
                reasons.append("Could not add user to group '{}', groep does not exist.".format(group))
            elif result.status_code == 103:
                reasons.append("Could not add user to group '{}', user does not exist.".format(group))
            elif result.status_code == 104:
                reasons.append("Could not add user to group '{}', insufficient privileges.".format(group))
            elif result.status_code == 105:
                reasons.append("Could not add user to group '{}', failed to add user to group.".format(group))
            else:
                reasons.append("Could not add user to group '{}', unknown error.".format(group))

        return True, "\n".join(reasons)


def get_available_groups():
    nc = NextCloud(endpoint=settings.NEXTCLOUD_URL, user=settings.NEXTCLOUD_USER, password=settings.NEXTCLOUD_PASSWORD, json_output=True)
    groups_res = nc.get_groups()
    if groups_res.status_code == 100:
        groups = groups_res.data['groups']
        return ((group, group) for group in groups)
    else:
        raise ValueError("Could not retrieve groups from NextCloud: Error {}".format(groups_res.status_code))


class GenerateInvitesForm(forms.Form):
    amount = forms.IntegerField(min_value=1, max_value=100)

    def __init__(self, *args, **kwargs):
        super(GenerateInvitesForm, self).__init__(*args, **kwargs)
        self.fields['groups'] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=get_available_groups(), required=False)

    def generate_codes(self):
        created = []
        groups = self.cleaned_data['groups']
        if not groups:
            groups = [settings.NEXTCLOUD_GROUP_NAME]
        for _ in range(self.cleaned_data['amount']):
            created.append(InviteCode.objects.create(used=False, used_by=None, groups=",".join(groups)))

        return self.cleaned_data['amount'], created
