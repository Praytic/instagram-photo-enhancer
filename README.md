# Instagram Photo Enhancer

This project has grown around the idea of converting high-quality photos to short videos (stories) with special effects. The first feature of this project – is **soft transition**. The idea behind it is to slowly transition one part of the image into another part. Soft transition can be handy when you need to show a horizontally (16:9) captured photo in vertical (9:16) format and you don't want to crop it or add black borders to it.

## Setup

_NOTE: This instruction has only been tested on aarch64 with Mac OS_

To setup this project on your local environment follow these steps:

1. Install mkcert.

    ```bash
    brew install mkcert
    brew install nss # if you use Firefox
    ```

1. Add mkcert to your local root CAs.

    ```bash
    mkcert -install
    ```

    This generates a local certificate authority (CA). Your mkcert-generated local CA is only trusted locally, on your device.

1. Generate a certificate, signed by mkcert. **Make sure you do it in the project root dir.**

    ```bash
    mkcert localhost
    ```

    The command above does two things:

    - Generates a certificate for the hostname you've specified
    - Lets mkcert (that you've added as a local CA in Step 2) sign this certificate.

1. Install python 3.9.16 with `pyenv`.

    ```bash
    brew install pyenv # if not yet installed
    pyenv install 3.9.16
    python -V
    ```

1. Install requirements for Flask server with `pip`. **Make sure you do it in the project root dir.**

    ```bash
    python -m ensurepip --upgrade
    pip install -r requirements.txt
    ```

1. Create `.env` file with the following variables:

    ```bash
    CLIENT_SECRET=
    CLIENT_ID=
    REDIRECT_URI=https://localhost:5000/callback
    ```

    Provide your own secrets from the developer console following this [guide](https://developers.facebook.com/docs/instagram-basic-display-api/) or request production secrets from the repo owners.

## Run

To run the project locally you need to execute the following command in the terminal. **Make sure you do it in the project root dir.**

```bash
python app.py
```

This will spin up a local web server and will serve static files from `./static` folder.

Now you can open `https://localhost:5000` in your browser and login with your instagram account.
