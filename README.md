# Aurvee Event Photo Sharing

Aurvee's locally hosted event photo-sharing app. The photographer uploads a group of pictures and displays its QR code. Guests scan it on the same Wi-Fi network to view the gallery and download the original files.

## Before you begin

You need:

- A Mac or Windows laptop.
- Python 3.10 or later.
- Node.js 18 or later (includes npm).
- An internet connection for the first dependency installation. The app's local photo-sharing flow does not need internet after setup.
- A Wi-Fi network that lets guest devices connect to the laptop. Some event networks block connections between devices; test the venue network before the event.

Check that Python and Node.js are available from a terminal:

```sh
python3 --version
node --version
npm --version
```

On Windows Command Prompt, use `py --version` if `python3` is not recognized.

## First-time setup on macOS

Open **Terminal**. Run the backend commands first. They create a private Python environment for this project, install Django and the image libraries, and create the local database:

```sh
cd "/Users/bhanuprakash/Desktop/PLV Content/personal/cameratrans/backend"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
deactivate
```

Now install the frontend packages:

```sh
cd "/Users/bhanuprakash/Desktop/PLV Content/personal/cameratrans/frontend"
npm install
```

Run these installation steps once per checkout. Run `npm install` again only if the frontend dependencies change. The database is created at `backend/db.sqlite3`; uploaded photos are stored under `backend/media/`.

## Start the app on macOS

After the first-time setup, start both local servers by either:

- Double-clicking `start-macos.command` in Finder. If macOS blocks it, right-click the file and choose **Open**.
- Or opening Terminal in the project folder and running:

```sh
cd "/Users/bhanuprakash/Desktop/PLV Content/personal/cameratrans"
./start-macos.command
```

The script runs database migrations, starts Django and Vite, and opens the dashboard. The dashboard normally opens at `http://localhost:5173`. Keep the terminal window open while the app is in use. If Vite reports a different port because 5173 is already occupied, open the URL Vite prints in Terminal.

To stop the app, focus the Terminal window running the script and press **Control+C**. This stops Vite and the backend server.

## First-time setup on Windows

Open **Command Prompt**. Create the backend environment, install its dependencies, and initialize the database:

```bat
cd /d "C:\path\to\cameratrans\backend"
py -3 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python manage.py migrate
deactivate
```

Replace `C:\path\to\cameratrans` with the folder where you saved the project. Then install the frontend packages:

```bat
cd /d "C:\path\to\cameratrans\frontend"
npm install
```

## Start the app on Windows

Double-click `start-windows.bat` in File Explorer. It opens a backend Command Prompt window, starts the frontend server, and opens the dashboard in your browser. Keep both windows open during an event. If Vite prints an address other than `http://localhost:5173`, use the address it prints.

To stop the app, press **Control+C** in the Command Prompt running the frontend, confirm if prompted, then close the backend Command Prompt window.

## Share a gallery with guests

1. Connect the laptop to the event Wi-Fi, or to a laptop hotspot configured for guest access.
2. Open the dashboard on the laptop. It should show the laptop's local network IP address.
3. Enter a gallery name, choose the photos, and set how long the gallery should remain available. Photos may be JPG/JPEG, PNG, or WebP, up to 25 MB each.
4. Optionally select a transparent PNG frame. SnapQR keeps the originals unchanged and provides a separate framed PNG download. The frame is fitted to each photo's dimensions.
5. Choose **Upload & create QR**. Keep the dashboard and both servers running.
6. Guests connect to the same Wi-Fi network, scan the QR code with their phone camera, and download the original photo. If a frame was used, they can download that framed copy too.
7. Use **Close & clear** to end the gallery early and delete its uploaded photos. Otherwise, the gallery becomes inaccessible at the selected expiry time.

The QR opens the laptop's network address, not `localhost`. Guests must be able to reach the laptop over the selected network. Their phones do not need an app or internet access.

## How to end a gallery or stop the app

### End the current gallery and delete its photos

On the photographer dashboard, select **Close & clear** and confirm. The QR link stops working and the gallery's uploaded originals, previews, and framed copies are deleted from the laptop. You can then upload a different group. Guests who already downloaded a file keep their own copy.

### Stop the app completely

- **macOS:** In the Terminal window running `start-macos.command`, press **Control+C**. This stops both local servers. If you started the script by double-clicking it, use the Terminal window that opened for it.
- **Windows:** Press **Control+C** in the Command Prompt running the frontend and confirm if prompted. Then close the separate **SnapQR backend** Command Prompt window.

When the app is stopped, guests cannot open galleries, even if their expiry time has not passed. If you restart the app before a gallery expires, that gallery remains available unless you used **Close & clear**.

## Expiry and storage behavior

The server stops serving a gallery as soon as it expires. While the dashboard is open, it checks for expired galleries every 15 seconds and deletes their uploaded files. If the dashboard is closed while the server remains running, expired files are removed the next time the batch list is requested. Closing a gallery manually deletes it immediately.

Downloads preserve the exact uploaded original file. Gallery previews are smaller for faster loading. Download tracking records that the server delivered a file; it cannot confirm that the guest saved it successfully on their phone. Keep separate backups of originals that you need to retain after a gallery closes.

## Troubleshooting

### The startup script says setup is missing

Complete the first-time setup steps for your operating system. Confirm that `backend/.venv` and `frontend/node_modules` exist, then run the startup script again.

### `pip install` cannot connect or resolve PyPI

The first setup needs internet access to download Python dependencies. Connect to the internet and rerun the install command from the `backend` folder with the virtual environment activated.

### `npm run dev` or `vite` is not found

Run `npm install` from the `frontend` folder, then restart the app.

### A phone cannot open the QR link

- Check that the phone and laptop are on the same Wi-Fi network.
- Keep the laptop awake and keep both server windows running.
- Allow incoming connections if the laptop firewall asks.
- Some guest Wi-Fi networks isolate devices. Try another network or a laptop hotspot that allows connected phones to reach the laptop.
- Do not replace the QR address with `localhost` or `127.0.0.1`; those addresses refer to the phone itself.

### The dashboard reports that no LAN address is available

Connect the laptop to Wi-Fi, wait a few seconds, then refresh the dashboard. The app cannot create a guest-accessible QR while it only sees a loopback address.

## Development and security notes

The startup scripts run Django's development server and Vite's development server. This is a local development setup, not a packaged production installer. Do not expose these servers to the public internet. The current first version has no photographer login; use it only on a trusted local network and test it at the venue before relying on it for an event.

The laptop hosts all photos. Guests who can reach the local server and know a gallery URL can access that gallery until it closes or expires. Django admin is not needed for normal use.
