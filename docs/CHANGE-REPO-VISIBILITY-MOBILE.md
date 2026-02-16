# How to Change Repository Visibility on Mobile

This guide explains how to change a GitHub repository from private to public (or vice versa) using a mobile device.

## Overview

GitHub repository visibility can be changed in two ways on mobile:
1. **Using the GitHub Mobile App** (recommended)
2. **Using a mobile web browser**

**Important Notes:**
- You must be the repository owner or have admin access
- Making a repository public will make all code, issues, and commits visible to everyone
- You cannot make a repository public if it contains forks of private repositories
- Free GitHub accounts have unlimited public and private repositories

---

## Method 1: Using GitHub Mobile App

The GitHub mobile app provides the most streamlined experience for changing repository settings.

### Prerequisites
- Download the GitHub app from [App Store](https://apps.apple.com/app/github/id1477376905) (iOS) or [Google Play](https://play.google.com/store/apps/details?id=com.github.android) (Android)
- Sign in to your GitHub account

### Steps

1. **Open the GitHub Mobile App**
   - Launch the GitHub app on your device
   - Ensure you're signed in to your account

2. **Navigate to Your Repository**
   - Tap the **menu icon** (three horizontal lines) in the top-left corner
   - Tap **"Your repositories"** or search for your repository name
   - Tap on the repository you want to change (e.g., `claws-and-pincers`)

3. **Access Repository Settings**
   - On the repository page, tap the **three dots** (⋯) in the top-right corner
   - Scroll down and tap **"Settings"**
   
   *Note: If you don't see Settings, you may not have admin access to the repository*

4. **Navigate to Visibility Settings**
   - Scroll down to the **"Danger Zone"** section at the bottom of the settings page
   - Tap **"Change repository visibility"**

5. **Change Visibility**
   - You'll see current visibility status (Private or Public)
   - Tap **"Change visibility"**
   - Select **"Make public"** (or "Make private" if changing to private)

6. **Confirm the Change**
   - GitHub will show you a confirmation dialog explaining the implications
   - Read the warning carefully
   - Type the repository name exactly as shown to confirm
   - Tap **"I understand, change repository visibility"**

7. **Verification**
   - You should see a success message
   - The repository page will now show a "Public" badge
   - Anyone can now view your repository at `https://github.com/Dutchthenomad/claws-and-pincers`

---

## Method 2: Using Mobile Web Browser

If you prefer not to use the app, you can change visibility through your mobile browser.

### Steps

1. **Open GitHub in Your Mobile Browser**
   - Navigate to [github.com](https://github.com) in Safari, Chrome, or your preferred browser
   - Sign in to your account if not already logged in

2. **Access Repository Settings**
   - Tap the **menu icon** (☰) to open the navigation
   - Navigate to **"Your repositories"**
   - Tap on the repository you want to change
   - Scroll down and tap **"Settings"** (may need to scroll right in the top tab menu)
   
   *Tip: If Settings tab is hidden, tap the "..." menu in the repository tabs*

3. **Navigate to Visibility Settings**
   - Scroll down to the bottom of the settings page
   - Find the **"Danger Zone"** section
   - Tap **"Change visibility"** or **"Change repository visibility"**

4. **Change to Public**
   - A modal dialog will appear
   - Select **"Make this repository public"**
   - Read the implications carefully

5. **Confirm the Change**
   - Type the repository name exactly as shown (e.g., `Dutchthenomad/claws-and-pincers`)
   - Tap **"I understand the consequences, change repository visibility"**

6. **Verification**
   - The page should refresh
   - You'll see a "Public" label next to your repository name
   - The repository is now publicly accessible

---

## Troubleshooting

### "Settings" Option Not Visible
- **Cause**: You don't have admin permissions for the repository
- **Solution**: Contact the repository owner to grant you admin access, or ask them to change the visibility

### Cannot Type Repository Name
- **Cause**: Mobile keyboard issues or browser compatibility
- **Solution**: 
  - Try refreshing the page
  - Use "Request Desktop Site" option in your browser
  - Switch to the GitHub mobile app
  - Try a different browser

### "This repository cannot be made public" Error
- **Cause**: Repository may contain forks of private repositories
- **Solution**: Remove private repository forks before making public

### Request Desktop Site (Fallback)
If the mobile interface is not working:
1. In your mobile browser, tap the **menu** (⋮ or share icon)
2. Enable **"Request Desktop Site"** or **"Desktop Mode"**
3. The full GitHub desktop interface will load
4. Follow the desktop instructions for changing visibility

---

## After Changing to Public

Once your repository is public:

✅ **What changes:**
- Anyone can view, clone, and fork your repository
- Repository appears in GitHub search results
- Code, issues, pull requests, and wiki are publicly visible
- Repository shows in your public profile

❌ **What stays protected:**
- Only collaborators can push changes
- Settings and admin actions remain restricted to authorized users
- Private repository secrets remain private (but review before making public)

---

## Security Checklist Before Making Public

Before changing a private repository to public, review:

- [ ] No API keys, tokens, or credentials in code or commit history
- [ ] No sensitive data in issues or pull requests
- [ ] No confidential information in README or documentation
- [ ] All environment variables properly configured (not hardcoded)
- [ ] Reviewed `.gitignore` to ensure sensitive files are excluded
- [ ] Comfortable with all commit history being public

**Tip**: Use `git log` and search for common secret patterns before going public.

---

## Related Documentation

- [GitHub Official: About repository visibility](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility)
- [GitHub Mobile App Documentation](https://docs.github.com/en/get-started/using-github/github-mobile)
- [Managing repository settings](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings)

---

## Quick Reference

| Task | GitHub App | Mobile Browser |
|------|------------|----------------|
| Access Settings | Repo → ⋯ → Settings | Repo → Settings tab |
| Change Visibility | Settings → Danger Zone → Change visibility | Settings → Danger Zone → Change visibility |
| Confirmation | Type repo name → Confirm | Type repo name → Confirm |
| Time Required | ~1 minute | ~2 minutes |

---

*Last Updated: 2026-02-16*
*Repository: Dutchthenomad/claws-and-pincers*
