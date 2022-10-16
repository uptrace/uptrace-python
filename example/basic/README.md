# Basic OpenTelemetry Python example

To run this example, you need to install OpenTelemetry distro for Uptrace:

```shell
pip install uptrace
```

The run the example passing Uptrace DSN in env variables:

```bash
UPTRACE_DSN="https://<token>@uptrace.dev/<project_id>" python3 main.py
```

## SSL

If you are getting SSL errors like this:

```
ssl_transport_security.cc:1468] Handshake failed with fatal error SSL_ERROR_SSL: error:1000007d:SSL routines:OPENSSL_internal:CERTIFICATE_VERIFY_FAILED
```

Try to use different root certificates as a [workaround](https://github.com/grpc/grpc/issues/27727):

```shell
export GRPC_DEFAULT_SSL_ROOTS_FILE_PATH=/etc/ssl/certs/ca-certificates.crt
```
