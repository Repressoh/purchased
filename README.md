# purchased
Automatically retrieve licenses for apps on the Apple App Store.

> [!NOTE]
> This tool **DOES NOT** promote piracy in any way and is not intended to cause harm. Use this at your own risk!

# What is This?

This is a little Python project I made to automate iTunes 12.6.5.3 on Windows after I discovered there were seemingly no tools publicly available to programmaticallly obtain licenses for Apple AppStore apps.

This was my first time using Python, therefore the code is probably not the best and might have some security issues.

# How do I set this up?

> [!IMPORTANT]
> Uninstall all other versions of iTunes, Bonjour, Apple Application Support, Apple Mobile Device Support Apple Software Update, iCloud and any other app possibly correlated.

1) Install iTunes 12.6.5.3

- [iTunes 12.6.5.3 Windows x64](https://secure-appldnld.apple.com/itunes12/091-87819-20180912-69177170-B085-11E8-B6AB-C1D03409AD2A6/iTunes64Setup.exe)
- [iTunes 12.6.5.3 Windows x86](https://secure-appldnld.apple.com/itunes12/091-87820-20180912-69177170-B085-11E8-B6AB-C1D03409AD2A5/iTunesSetup.exe)

2) Enable "Apps" Section

First, click on this menu.

![menu 1](https://github.com/user-attachments/assets/c5babc65-39eb-4121-aa22-2550cf52e257)

Then click "Edit Menu", select the sections you are interested in **plus** the "Apps" section and click "Done".

![select apps section](https://github.com/user-attachments/assets/cad61c28-b696-45ce-902f-8e7ea64b97de)

That done, switch to the "Apps" section before proceeding.

3) Logging In

Once on the "Apps" section, click on the "Account" menu on the top and select "Sign In...".

![sign in](https://github.com/user-attachments/assets/471d1343-87e9-4072-a27a-8a98a8f909f1)

On the popup that appears, login with your Apple ID.

![login popup](https://github.com/user-attachments/assets/f44d4435-4bb7-4668-aba4-c8d78752c5eb)

Once Logged In, go back on the "Account" menu to the top and select "Authorizations" and "Authorize this computer...".

![authorizing computer](https://github.com/user-attachments/assets/8ec3847b-da04-4813-a661-8ccd3543a4d9)

When prompted to Sign In again, do so.

![authorising computer login](https://github.com/user-attachments/assets/27b73832-aa8e-471b-a2ae-7b9bd0e47b63)

Once that is done, a PopUp confirming the computer has been authorized succesfully will appear.

![authorization confirmation](https://github.com/user-attachments/assets/e81db673-593f-455b-afbc-1805fdc74e4c)

4) Tweaking Settings

Now, head to the "Edit" menu to the top and select "Preferences...".

![preferences menu](https://github.com/user-attachments/assets/27dae0c7-ba53-4eb3-819c-1e0d323a3805)

There, go to the "Store" tab and switch "Purchases:" and "Free Downloads:" to "Never Require".

![never require setting](https://github.com/user-attachments/assets/aee8adf6-27f7-4cf5-82f4-1938d8b4f3a0)

When clicking on "Ok" to confirm your choices, it might prompt you to re-enter your login and/or confirm your 2FA.

5) Install the automation

Now, get a copy of the repo by either using git or downloading a copy of the repository.

```
git clone https://github.com/Repressoh/purchased
```

Once that is done, you need to get a postgresql database to store the "jobs" and other stuff. I can't provide a specific guide for this, but any postgresql host should be fine.

When you have the database, open the "main.py" file and replace the "< your-database-url >" with your database connection string.

```
db_pool = pool.SimpleConnectionPool(1, 20, "postgresql://[user[:password]@][netloc][:port][/dbname]")
```

That's it! Now you are free to run the script and start making requests.

# Contributions

To contribute, please create a Pull Request.

# issues

If you face any issues or weird errors, feel free to open an issue.

# Legal

For any legal concerns, feel free to reach out to me at me@repressoh.eu.org.
