from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import redirect


class HydroServerSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        if not sociallogin.is_existing:
            # print(sociallogin.account)
            print(sociallogin.account.extra_data)
            # if not sociallogin.account.extra_data.get('email'):
            #     # Save social login data in session and redirect to email form
            #     request.session['sociallogin'] = sociallogin.serialize()
            #     return redirect('account_email_selection')  # Your custom email form
