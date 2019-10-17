<img src="favicon.png" width=200>

# SX Google Drive Token Generator

This Python script/app is used to simplify the process of creating an OAuth token file for use with SX Installer homebrew app on the Nintendo Switch. SX Installer v3.00 added authenticated Google Drive support via **`gdrive:/`** paths. Despite this, Xecuter does not appear to have posted any instructions on how to actually make use of the new feature. By poking around in the .nro file, I eventually figured out its usage. This utility should make it quick and easy to create the necessary files to make use of this new feature.

Note: I suspect other variants of Tinfoil will shortly add authenticated Google Drive support (if they don't already). It is very likely that the setup process will be nearly identical if that happens, but I will update this info if I learn of any developments in this regard.


## Requirements

### Python script version

* Python 3.7+
* Python Packages:
    * oauth2client
    * google-api-python-client

### EXE version

* None


## Generating OAuth Credentials

Before adding an authenticated Google Drive folder to SX Installer, you will first need to generate your OAuth credentials/token files and transfer them to your Switch Micro SD.

* Download and extract the latest version of the Python script or EXE version from [SxGDriveTokenGenerator Releases](https://github.com/lahma69/SxGDriveTokenGenerator/releases)
* Ensure you are logged into the relevant Google Drive account and navigate to https://developers.google.com/drive/api/v3/quickstart/python
* Complete **Step 1**, clicking the **Download Client Configuration** button when it appears, and save the **credentials.json** file to the same directory you extracted the app package to
* Run the Python script or EXE (depending on which you downloaded)
* Follow the prompts in the app cmd/shell window to verify your OAuth credentials (the app will open a browser window to complete this process)
* After the app completes and the cmd/shell window closes, ensure the following 2 files exist:
    * **[App/Script-Directory]/switch/sx/credentials.json**
    * **[App/Script-Directory]/switch/sx/gdrive.token**
* From the app directory, copy the **switch** folder to the root of your Switch Micro SD card
* At the conclusion of this process, you should have the files **credentials.json** and **gdrive.token** in the directory **/switch/sx** on your Switch Micro SD

Note: You should delete or move any .JSON files from the app directory to a safe location. With these files, an unauthorized party could gain access to all of the files on your Google Drive.


## Adding a Google Drive Folder to SX Installer

After generating your credentials/token files and transferring them to your Micro SD, you will need to add a Google Drive path to SX Installer. You can do this through either the SX Installer UI or by manually adding a path to your SX Installer **locations.conf** file.

To add a **File Browser** entry to SX Installer that points to the root of your Google Drive, you simply leave use a blank **gdrive** path: `gdrive:/`. If you're adding a **File Browser** entry via the SX Installer UI, simply leave the **Path** element empty.

If however you want to add an entry that points to a specific folder in your Google Drive, you first need to get the ID of this folder. Foruntately, this is very easy to do. Simply open https://drive.google.com, navigate to the desired folder, and then look at your browser's address bar. You will see a URL in the format of: `https://drive.google.com/drive/folders/XXXXXXXXXXXX`. The long string of characters (represented by X's in this example) is your folder's ID.

If you're adding a **File Browser** entry using the SX Installer UI, insert your folder's ID into the **Path** element. If you're adding an entry by modifying your **locations.conf** file, insert your folder's ID following the 'gdrive:/' text such as in this example: `gdrive:/XXXXXXXXXXXXX`.

### Add via SX Installer UI

To create a **File Browser** entry that points to the root directory of your Google Drive, do the following:

* Open SX Installer
* Scroll down to **File Browser** and hit **(A)** button
* Hit **(-)** button
* Select **Protocol**, hit **(A)** button, press down until **gdrive** is selected, and then hit the **(A)** button
* Select **Title**, hit **(A)** button, type in whatever name you want, and then hit the **(+)** button
* Hit the **(X)** button to save the entry

Note: If you wanted the entry to point to a specific folder instead of the root of your Google Drive, before saving the entry, you would enter your folder's ID into the **Path** element.

### Add via **locations.conf**

Here are a few examples of a **locations.conf** file to demonstrate the use of Google Drive paths. The relevant parts will appear in **bold** font. In the examples below, the **enabled** variable defines whether you want SX Installer to automatically load/scan the URL at startup. I'm not entirely sure if SX Installer even pays attention to this value on **gdrive** entries.

<p align="center"><b>Simple entry that points to the root of your Google Drive</b></p>

<code>["usb:/","usbfs:/","sdmc:/","usbhdd:/",<b>"gdrive:/"</b>]</code>

<p align="center"><b>Custom 'Display Name' - points to root of your Google Drive</b></p>

<code>["usb:/","usbfs:/","sdmc:/","usbhdd:/",<b>{"url":"gdrive:/","title":"GDrive-root","enabled":1}</b>]</code>

<p align="center"><b>Point to specific Google Drive folder</b></p>

Note: Substitute the X's with your folder's ID.

<code>["usb:/","usbfs:/","sdmc:/","usbhdd:/",<b>{"url":"gdrive:/XXXXXXXXXX","title":"GDrive-Homebrew","enabled":1}</b>]</code>


## Config File

Custom values can be provided to the app through the use of a JSON config file. By default, the app will attempt to load **config.json** from the app directory and if it is not found, a new config file will be generated using default values. A user-defined path to the config file can also be used by providing the config file path as an argument to the app:
`python GenerateSxiGdCreds.py "Documents/gsxigdcreds_config.json"`.
Continue below for additional info.

### Config File - Key/Values

<table>
    <thead>
        <tr>
            <th><b>Key</b></th>
            <th><b>Default Value</b></th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><b>"client_secret_json_paths"</b></td>
            <td>["credentials.json", "client_secret*.json"]</td>
        </tr>
        <tr>
          <td colspan=2>All values in this array will be searched in order until a match is found. Paths support wildcards (*) in the filename part of the path (not directory). For example, the default value <b>"client_secret*.json"</b> will match a file named <b>client_secret_XX-XX.apps.googleusercontent.com.json</b>. If multiple wildcard matches are found, the 1st will be used. Windows paths <b>must</b> be separated with double backslashes (\\) or forwardslashes (/).</td>
        </tr>
        <tr>
            <td><b>"output_folder_path"</b></td>
            <td>"switch/sx/"</td>
        </tr>
        <tr>
          <td colspan=2>This is where the token and credentials file will be written to. The default path makes it easy to copy the <b>switch</b> folder to the root of your SD. Your client secret JSON is renamed/copied to the output folder as <b>credentials.json</b>. The output token file is named <b>gdrive.token</b>.</td>
        </tr>
        <tr>
            <td><b>"scopes"</b></td>
            <td>["https://www.googleapis.com/auth/drive.readonly"]</td>
        </tr>
        <tr>
          <td colspan=2>This value should be not be changed unless you have a good reason to do so. SX Installer uses the <b>readonly</b> scope and does not support writing anyways. Keeping it <b>readonly</b> means your files cannot be modified/deleted if your token is stolen.</td>
        </tr>
        <tr>
            <td><b>"output_token_json_name"</b></td>
            <td>"gdrive.token"</td>
        </tr>
        <tr>
          <td colspan=2>The name of the output token file. This should not be changed or SX Installer will not find it.</td>
        </tr>
        <tr>
            <td><b>"output_client_secret_json_name"</b></td>
            <td>"credentials.json"</td>
        </tr>
        <tr>
          <td colspan=2>The name of the output/copied client secret file. This should not be changed or SX Installer will not find it.</td>
        </tr>
    </tbody>
</table>


## Additional Info

* The client secrets JSON file can be named anything but most commonly it will be named one of the following:
    * **credentials.json**
    * **client_secret.json**
    * **client_secret_XXXXX-XXXXX.apps.googleusercontent.com.json**.
* SX Installer requires the following 2 files to be located on the SD at **'/switch/sx/'** for authenticated Google Drive paths to work:
    * **gdrive.token**
    * **credentials.json**
