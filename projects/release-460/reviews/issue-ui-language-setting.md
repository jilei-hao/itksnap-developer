### What happens

ITK-SNAP chooses its user-interface language from the operating system. Some users get a language they did not choose, and have no easy way to change it:

- In #210, a Mac set to English but located in Germany showed ITK-SNAP in German. The macOS per-application language setting did not fix it for the reporter; changing the Mac's region to the US did.
- In the same issue, a Windows user got Spanish, and had to change the Windows display language to get English.

Today the only override is the `--lang` command-line option. That is hard to use when ITK-SNAP starts from the Dock, the Start menu or a double-clicked file. Windows has no per-application language setting at all.

### Proposal

Add a **Language** setting to Preferences, on the General tab:

- The choices are **Automatic** (today's behavior) followed by every translation that ships with ITK-SNAP. Each language is written in that language: English, Deutsch, Español, 简体中文. That way, someone stuck in a language they cannot read can still find their own.
- It takes effect the next time ITK-SNAP starts, and the dialog says so. Switching the language of open windows on the fly would mean re-translating every window, and ITK-SNAP does not do that today.
- Order of priority: `--lang` on the command line, then this setting, then Automatic.
- It is saved with the other preferences.

Nothing changes for users who leave it on Automatic.

### Question for maintainers

Should the setting change only the translation, or also number and date formats?

- `--lang` does both today (`QLocale::setDefault`).
- We suggest the translation only, so that choosing English on a German system keeps the decimal comma the region expects.
- If `--lang` and the setting should behave the same, that is easy to do instead.

### Relation to #255

#255 changes how the Automatic language is detected. This proposal is independent of it: it keeps the automatic choice as it is, and adds a way for each user to override it. The two could land separately.

We have started on this in the `feature/ui-language-setting` branch of jilei-hao/itksnap, and will open a pull request that references this issue.
