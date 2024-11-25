# Framenet Umbrella - Version 0.0.1

© 2025 Framenet Umbrella, by FinDev

Framenet Umbrella is a DNS filtering service that blocks specific domains and serves a custom block page for users who try to access these domains. It also includes an admin panel for managing the block list.

## Features:
- DNS server that blocks requests for specific domains.
- Web-based admin panel for adding/removing domains to/from the block list.
- Customizable block page with logo.
- Supports both local and external IP addresses for the server.

---

## Installation

To run Framenet Umbrella, you need to install the required dependencies:

1. **Install `dnslib` and `Flask`:**
    ```bash
    pip install dnslib flask
    ```

2. **Download the source code:**
    Clone the repository to your local machine:
    ```bash
    git clone https://github.com/JaidenDev/Framenet-Umbrella.git
    cd Framenet-Umbrella
    ```

---

## Configuration

### 1. Changing the DNS Server's IP

The server IP address must be updated to the local or external IP of the machine where Framenet Umbrella is running. This IP will be used in the DNS response for blocked domains.

- **Locate the following line** in the DNS handler code:
    ```python
    SERVER_IP = "127.0.0.0"
    ```

- **Update `SERVER_IP`** with your server's local or external IP address.

### 2. Changing the Admin Login Credentials

By default, the admin credentials are set to:
- Username: `admin`
- Password: `admin`

You can change these by modifying the following lines in the Flask application code:

- **Locate the credentials section:**
    ```python
    USERNAME = 'admin'
    PASSWORD = 'admin'
    ```

- **Update `USERNAME` and `PASSWORD`** with your desired credentials.

### 3. Block List File

Framenet Umbrella uses a JSON file to store the list of blocked domains. The file `block_list.config` is loaded at runtime, and you can modify it directly or manage it via the admin panel.

- **Location of the block list file**: `block_list.config`
- You can manually edit this file or use the web admin interface to add/remove domains.

---

## Usage

1. **Run the DNS Server**:
    The DNS server listens on port 53, and the HTTP server serves the block page on port 80. To start both services, run the script:

    ```bash
    python3 framenet_umbrella.py
    ```

    The DNS server will block requests for any domains listed in `block_list.config`, while the HTTP server will show a custom block page.

2. **Access the Admin Panel**:
    The admin panel is accessible via a web browser:
    - Go to `http://<server_ip>:8800`
    - Login with the credentials you set up.

    Once logged in, you can:
    - Add or remove domains to/from the block list.
    - View the list of currently blocked domains.

3. **Serve Block Page**:
    If a user attempts to access a blocked domain, they will be served a custom block page that includes the blocked domain name, a reason (if provided), and your logo.

---

## Notes

- **Server IP**: Make sure the server’s IP address is correctly configured, as this is crucial for the DNS server to function properly.
- **Admin Login**: Make sure to update the admin credentials before deploying the server publicly.
- **Dependencies**: Ensure that `dnslib` and `flask` are installed to run both the DNS server and the web admin panel.

---

## License

© 2025 Framenet Umbrella, by FinDev

---

## Contributing

Feel free to fork, submit issues, and send pull requests. Contributions are welcome!

---

## Contact

jaiden@jaiden.pro