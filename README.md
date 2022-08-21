# Synapse

Synapse randomly pairs people in an organization for 1-on-1's on a regular schedule.

## Setup

- Install Poetry
- Install dependencies: `poetry install`
- Use Poetry environment: `poetry shell`

## Usage

```bash
poetry run synapse
```

More examples:

- Help `poetry run synapse --help`
- Don't send emails: `poetry run synapse --no-send`

### Options

- `--no-send`: Do not actually send emails.
- `--send`: Send emails without confirmation.
- `--spreadsheet`: The Google Spreadsheet ID to save output to.
- `--sheet`: The Google Spreadsheet Sheet ID to save output to. Utilizes relevant environment variable if not provided. Defaults to 0 if neither supplied.

### Environment variables

- `SYNAPSE_SPREADSHEET`
- `SYNAPSE_SHEET`
- `SYNAPSE_GOOGLE_SERVICE_ACCOUNT`: The JSON token for the Google service account that has access to the Google Drive and Google Sheets.
  - The format should be something like this; make sure to escape double quotes and new line characters (or remove): \
    ```bash
    GOOGLE_SERVICE_ACCOUNT="{
      \"type\": \"service_account\",
      \"private_key\": \"-----BEGIN PRIVATE KEY-----\\nXXXX...YYYY\\n-----END PRIVATE KEY-----\\n\",
      \"client_email\": \"project@project.iam.gserviceaccount.com\",
      \"auth_uri\": \"https://accounts.google.com/o/oauth2/auth\",
      \"token_uri\": \"https://oauth2.googleapis.com/token\",
      \"auth_provider_x509_cert_url\": \"https://www.googleapis.com/oauth2/v1/certs\",
      \"client_x509_cert_url\": \"https://www.googleapis.com/robot/v1/metadata/x509/project%40project.iam.gserviceaccount.com\"
    }"
    ```
  - Make sure the email for the service account is shared with the document that is meant to be written to.
  - Helpful reference: [gspread auth](https://docs.gspread.org/en/latest/oauth2.html)

## Contributing

See [docs/CONTRIBUTING.md](./docs/CONTRIBUTING.md).

## License

Licensed under the [LGPL 3.0](https://www.gnu.org/licenses/lgpl-3.0.en.html); see [LICENSE.txt](./LICENSE.txt) for details.
