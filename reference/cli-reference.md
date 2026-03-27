# Viam CLI Reference

Complete command reference for the Viam CLI (`viam`), built on urfave/cli v2.

**Entry point**: `cli/viam/main.go`
**Source**: `~/viam/rdk/cli/`

## Global Flags

| Flag | Alias | Description |
|------|-------|-------------|
| `--base-url` | | Custom API endpoint URL (hidden) |
| `--config`, `-c` | | Load configuration from file |
| `--debug`, `-vvv` | | Enable debug logging |
| `--quiet`, `-q` | | Suppress warnings |
| `--profile` | | Use a specific CLI profile for this command |
| `--disable-profiles` | `--disable-profile` | Disable profile-based auth, fall back to default behavior |

---

## 1. `login` (alias: `auth`)

**Summary**: Authenticates to the Viam platform (app.viam.com). Uses OAuth 2.0 device code flow: opens a browser, you confirm a code, and the CLI caches an access token locally. Tokens auto-refresh. Also supports headless API key authentication.

**Use cases**: First thing you run after installing the CLI. Required before any command that talks to the Viam cloud.

**Implementation**: `cli/auth.go`

### Subcommands

| Command | Description |
|---------|-------------|
| `login` | Interactive browser-based OAuth login. Opens your default browser to confirm a device code. |
| `login --disable-browser-open` | Headless login. Prints a URL to visit manually (for SSH sessions, containers). |
| `login api-key --key-id=<id> --key=<secret>` | Non-interactive login with an API key. Validates the key by listing orgs. |
| `login print-access-token` | Prints the current OAuth bearer token to stdout. Only works with user tokens, not API keys. Useful for piping into other tools. |

### Examples

```bash
viam login
viam login --disable-browser-open
viam login api-key --key-id=abc123 --key=secret456
viam login print-access-token
```

---

## 2. `logout`

**Summary**: Clears locally cached auth credentials (OAuth token or API key) by deleting the config cache file.

**Implementation**: `cli/auth.go`

### Examples

```bash
viam logout
```

---

## 3. `whoami`

**Summary**: Prints the email of the currently authenticated user, or `key-<uuid>` if authenticated via API key.

**Implementation**: `cli/auth.go`

### Examples

```bash
viam whoami
# => user@example.com
# => key-937682a5-9710-4a0b-8f8b-02ed322e396f
```

---

## 4. `defaults`

**Summary**: Persists default org and location IDs in the CLI config so you don't have to pass `--org-id` and `--location-id` on every command. Validates that the org/location exists and is accessible before saving. Profile-aware: defaults are scoped to the active profile.

**Use cases**: Set defaults once for your primary org/location, then omit those flags from all subsequent commands.

**Implementation**: `cli/defaults.go`

### Subcommands

| Command | Description |
|---------|-------------|
| `defaults set-org --org-id=<uuid>` | Validates the org exists and saves it as the default. |
| `defaults clear-org` | Removes the default org. |
| `defaults set-location --location-id=<uuid>` | Validates the location exists (within the default org if set) and saves it as the default. Warns if no default org is set. |
| `defaults clear-location` | Removes the default location. |

### Examples

```bash
viam defaults set-org --org-id=abc123
viam defaults set-location --location-id=def456
viam defaults clear-org
viam defaults clear-location
```

---

## 5. `profiles`

**Summary**: Manages named authentication profiles, each backed by an API key. Profiles let you switch between orgs/accounts without logging out and back in. Activate a profile per-command with `--profile <name>` or per-session via the `VIAM_CLI_PROFILE_NAME` environment variable. Each profile stores its own auth config, default org, and default location independently.

**Use cases**: Operating across multiple Viam organizations (personal vs. work, dev vs. prod).

**Implementation**: `cli/profile.go`

### Subcommands

| Command | Description |
|---------|-------------|
| `profiles add --profile-name=<name> --key-id=<id> --key=<secret>` | Creates a new named profile. Errors if the name already exists. |
| `profiles update --profile-name=<name> --key-id=<id> --key=<secret>` | Creates or overwrites a profile (upsert). Also updates the cached auth config for the profile. |
| `profiles list` | Lists all profile names. |
| `profiles remove --profile-name=<name>` | Deletes a profile and its cached config file. |

### Examples

```bash
viam profiles add --profile-name=prod --key-id=abc --key=secret
viam profiles list
viam machines list --profile=prod
export VIAM_CLI_PROFILE_NAME=prod
viam profiles remove --profile-name=prod
```

---

## 6. `organizations` (aliases: `organization`, `org`)

**Summary**: Manages Viam organizations: listing, API key creation, branding (logo/support email), billing, and OAuth application configuration.

**Implementation**: `cli/client.go`, `cli/auth.go` (OAuth app commands)

### Subcommands

#### Basic Operations

| Command | Description |
|---------|-------------|
| `organizations list` | Lists all organizations the current user belongs to, with IDs and names. |
| `organizations api-key create --org-id=<uuid>` | Creates an org-scoped API key with `organization_owner` role. Outputs the key ID and value. The key has full write access to the org. |

#### Branding

| Command | Description |
|---------|-------------|
| `organizations logo set --org-id=<uuid> --logo-path=<file>` | Uploads a PNG logo for the organization. Used in white-label/branded deployments. |
| `organizations logo get --org-id=<uuid>` | Retrieves the organization's logo. |
| `organizations support-email set --org-id=<uuid> --support-email=<email>` | Sets the org's support contact email. |
| `organizations support-email get --org-id=<uuid>` | Gets the org's support contact email. |

#### Billing

| Command | Description |
|---------|-------------|
| `organizations billing-service get-config --org-id=<uuid>` | Returns the billing service configuration for the org. |
| `organizations billing-service enable --org-id=<uuid> --address=<addr>` | Enables billing for the org. Address format: `"line1, line2 (optional), city, state, zipcode"`. |
| `organizations billing-service disable --org-id=<uuid>` | Disables billing for the org. |
| `organizations billing-service update --org-id=<uuid> --address=<addr>` | Updates the billing address. |

#### OAuth / Auth Service

| Command | Description |
|---------|-------------|
| `organizations auth-service enable --org-id=<uuid>` | Enables the OAuth 2.0 authorization service for the org. Required before creating OAuth apps. |
| `organizations auth-service disable --org-id=<uuid>` | Disables the OAuth authorization service. Prompts for confirmation. |
| `organizations auth-service oauth-app create` | Creates an OAuth application. Requires client authentication policy, PKCE setting, URL validation, redirect URIs, logout URI, and enabled grants. |
| `organizations auth-service oauth-app read --org-id=<uuid> --client-id=<id>` | Returns the full OAuth configuration for an app (auth policy, PKCE, URIs, grants). |
| `organizations auth-service oauth-app update --org-id=<uuid> --client-id=<id>` | Updates any subset of an OAuth app's configuration. |
| `organizations auth-service oauth-app delete --org-id=<uuid> --client-id=<id>` | Deletes an OAuth application. Prompts for confirmation. |
| `organizations auth-service oauth-app list --org-id=<uuid>` | Lists all OAuth applications for the org. |

### Examples

```bash
viam organizations list
viam org api-key create --org-id=abc123

viam org logo set --org-id=abc123 --logo-path=./logo.png
viam org support-email set --org-id=abc123 --support-email=help@example.com

viam org billing-service enable --org-id=abc123 --address="123 Main St, Springfield, IL, 62704"

viam org auth-service enable --org-id=abc123
viam org auth-service oauth-app create --org-id=abc123 \
  --client-authentication=required --pkce=required \
  --url-validation=exact_match \
  --redirect-uris=https://app.example.com/callback \
  --logout-uri=https://app.example.com/logout \
  --enabled-grants=authorization_code
```

---

## 7. `locations` (alias: `location`)

**Summary**: Lists locations within an org and creates location-scoped API keys. Locations are a grouping mechanism for machines within an organization.

**Implementation**: `cli/client.go`

### Subcommands

| Command | Description |
|---------|-------------|
| `locations list` | Lists locations for the current user. Uses the default org if set, otherwise the first org alphabetically. |
| `locations api-key create --location-id=<uuid>` | Creates a location-scoped API key with `location_owner` role. If the location belongs to multiple orgs, `--org-id` is required. |

### Examples

```bash
viam locations list --org-id=abc123
viam locations api-key create --location-id=def456
```

---

## 8. `machines` (aliases: `machine`, `robots`, `robot`)

**Summary**: The largest command group. Full lifecycle management for machines and their parts, plus remote connectivity features (shell access, file copy, port tunneling, motion control).

**Implementation**: `cli/client.go`, `cli/module_reload.go`

### What Are Machine Parts?

A machine in Viam can be composed of one or more **parts**. Each part is a separate instance of `viam-server` with its own configuration, and each part connects independently to the Viam cloud. Every machine has at least one part — the **main part** — which is created automatically when you create the machine.

Multi-part machines exist because a single robot may involve multiple computers. A mobile robot might have a Jetson running the arm and cameras, and a Pi running the drive base and wheel encoders. Each computer runs its own `viam-server` process as a separate part of the same logical machine. The parts communicate with each other over gRPC, and from the SDK's perspective the resources on all parts are accessible as if they were on a single machine.

Parts are the unit of configuration, connectivity, and logging. When you SSH into a machine, deploy a module, or read logs, you target a specific part. The main part's config lives at the machine level in the Viam app; sub-parts have their own configs. Each part has its own FQDN for direct connections and its own set of resources (components and services).

### Machine-Level Commands

| Command | Description |
|---------|-------------|
| `machines create --org-id=<uuid> --location-id=<uuid> --name=<name>` | Creates a new machine in the specified org and location. |
| `machines delete --machine-id=<uuid>` | Deletes a machine. |
| `machines update` | Moves a machine to a different location and/or renames it. |
| `machines list --org-id=<uuid> --location-id=<uuid>` | Lists all machines in a location. |
| `machines status` | Shows machine online/offline status. |
| `machines logs` | Displays machine logs. Supports filtering by level, keyword, and format (text/json). |
| `machines api-key create --machine-id=<uuid>` | Creates a machine-scoped API key with `robot_owner` role. |

### Part Management

| Command | Description |
|---------|-------------|
| `machines part create` | Creates a new part on a machine. |
| `machines part delete` | Deletes a part. |
| `machines part list` | Lists all parts on a machine. |
| `machines part status` | Shows a part's status. |
| `machines part logs` | Displays part-level logs. |
| `machines part restart` | Requests a part restart. |
| `machines part add-resource` | Adds a component or service to a part's configuration by specifying an API and model triple. |
| `machines part remove-resource` | Removes a resource from a part's configuration. |
| `machines part fragments add` | Attaches a configuration fragment to a part. Fragments are reusable config snippets shared across parts. |
| `machines part fragments remove` | Detaches a fragment from a part. |

### Remote Connectivity

| Command | Description |
|---------|-------------|
| `machines part run` | Executes a single gRPC method on a machine part. Specify the resource, method, and data payload. Like `curl` for Viam's gRPC API. |
| `machines part shell` | Opens an interactive SSH-like shell to a remote machine via Viam's WebRTC connection. Requires the machine to have a `shell` service. |
| `machines part cp` | Copies files to/from a remote machine part via the shell service. Supports `--recursive` and `--preserve`. Uses Viam's secure connection, not SSH. Path format: `machine:<path>`. |
| `machines part get-ftdc` | Downloads Full-Time Diagnostic Data Capture (FTDC) files from a machine part. FTDC is a compact binary format recording resource-level performance metrics. |
| `machines part tunnel --local-port=<port> --destination-port=<port>` | Creates a TCP tunnel from a local port to a port on the remote machine. Useful for accessing web UIs, databases, or other services on machines that aren't directly reachable. |

### Motion Control

| Command | Description |
|---------|-------------|
| `machines part motion print-config` | Prints the motion planning configuration for the part. |
| `machines part motion print-status` | Prints current motion state. |
| `machines part motion get-pose --component=<name>` | Retrieves a component's pose in a reference frame. |
| `machines part motion set-pose --component=<name>` | Commands a component to move to a specific pose. |

### Examples

```bash
viam machines list --org-id=abc123 --location-id=def456
viam machines create --org-id=abc123 --location-id=def456 --name=my-robot
viam machines update --machine-id=mach123 --new-name=renamed-robot --new-location=loc456

viam machines part shell --part=part-id-123
viam machines part cp --part=part-id-123 -r ./local-dir machine:/home/user/
viam machines part tunnel --part=part-id-123 --local-port=8080 --destination-port=8080

viam machines part run --part=part-id-123 \
  --data='{"name":"motor-1"}' --method=GoFor --component=rdk:component:motor
viam machines part motion get-pose --part=part-id-123 --component=arm-1

viam machines part fragments add --part=part-id-123 --fragment=frag456

viam machines logs --machine-id=abc123 --levels=error,warn --tail
```

---

## 9. `data`

**Summary**: Manages data stored in Viam's cloud data service. Covers exporting (downloading), deleting, tagging, querying the underlying MongoDB Atlas Data Federation database, and managing indexes on data collections.

**Implementation**: `cli/data.go`, `cli/app.go` (index commands)

### Export

| Command | Description |
|---------|-------------|
| `data export binary filter` | Downloads binary data (images, point clouds, etc.) matching a set of filters. Supports parallel downloads (`--parallel`, default 100). Filters: org, location, machine, part, component type/name, method, time range, mime types, bounding box labels, tags. |
| `data export binary ids --binary-data-ids=<id1>,<id2>` | Downloads specific binary data items by their IDs. |
| `data export tabular` | Downloads tabular (sensor) data for a specific part + resource + method. Writes newline-delimited JSON (`data.ndjson`). Requires `--part-id`, `--resource-name`, `--resource-subtype`, and `--method`. |

### Delete

| Command | Description |
|---------|-------------|
| `data delete binary` | Deletes binary data matching filters. Requires `--org-ids`, `--start`, and `--end`. |
| `data delete tabular --org-id=<uuid> --delete-older-than-days=<N>` | Deletes tabular data older than N calendar days. Pass `0` to delete all tabular data. |

### Database (MongoDB Atlas Data Federation)

| Command | Description |
|---------|-------------|
| `data database configure --org-id=<uuid> --password=<pw>` | Sets up or updates credentials for the org's MongoDB Atlas Data Federation instance. Warns if credentials already exist (changing them breaks existing dashboards and integrations). |
| `data database hostname --org-id=<uuid>` | Returns the MongoDB connection hostname and URI for the org's Data Federation instance. |

### Tagging

| Command | Description |
|---------|-------------|
| `data tag ids add --tags=<t1>,<t2> --binary-data-ids=<id1>,<id2>` | Adds tags to specific binary data items. |
| `data tag ids remove --tags=<t1>,<t2> --binary-data-ids=<id1>,<id2>` | Removes tags from specific binary data items. |
| `data tag filter add --tags=<t1>,<t2> [filter flags]` | Adds tags to all binary data matching a filter. Operates in bulk (100 concurrent requests). |
| `data tag filter remove --tags=<t1>,<t2> [filter flags]` | Removes tags from all binary data matching a filter. |

### Indexes

| Command | Description |
|---------|-------------|
| `data index create --org-id=<uuid> --collection-type=<type> --index-path=<file>` | Creates a MongoDB index on a data collection. `--collection-type` is `hot` (hot storage) or `pipeline_sink`. The index spec is a JSON file. |
| `data index delete --org-id=<uuid> --index-name=<name>` | Deletes an index from a data collection. |
| `data index list --org-id=<uuid> --collection-type=<type>` | Lists all indexes for a data collection. |

### Examples

```bash
# Export
viam data export binary filter --destination=./downloads --org-ids=abc123 --parallel=50
viam data export binary ids --destination=./downloads --binary-data-ids=id1,id2
viam data export tabular --destination=./sensor-data \
  --part-id=part123 --resource-name=accel \
  --resource-subtype=movement_sensor --method=LinearAcceleration

# Delete
viam data delete tabular --org-id=abc123 --delete-older-than-days=30

# Database
viam data database configure --org-id=abc123 --password=mypassword
viam data database hostname --org-id=abc123

# Tags
viam data tag ids add --tags=labeled,reviewed --binary-data-ids=id1,id2
viam data tag filter add --tags=needs-review --org-ids=abc123 --component-type=camera

# Indexes
viam data index create --org-id=abc123 --collection-type=hot --index-path=./index-spec.json
viam data index list --org-id=abc123 --collection-type=hot
```

---

## 10. `dataset`

**Summary**: Manages named collections of binary data for ML training. Datasets group binary data items together and can be exported with annotation metadata in JSONL format for training pipelines.

**Implementation**: `cli/dataset.go`, `cli/data.go` (data add/remove)

### Subcommands

| Command | Description |
|---------|-------------|
| `dataset create --org-id=<uuid> --name=<name>` | Creates a new empty dataset. Returns the dataset ID. |
| `dataset rename --dataset-id=<uuid> --name=<new-name>` | Renames an existing dataset. |
| `dataset list` | Lists datasets. Pass `--dataset-ids` for specific IDs, or `--org-id` for all in an org. |
| `dataset delete --dataset-id=<uuid>` | Deletes a dataset (does not delete the underlying binary data). |
| `dataset export --dataset-id=<uuid> --destination=<dir>` | Downloads all binary data in a dataset plus a `dataset.jsonl` file with annotations (classification labels, bounding boxes), timestamps, and file paths. The JSONL format is what Viam's training infrastructure consumes. Supports `--only-jsonl` (metadata only, skip binary files) and `--force-linux-path` (forward slashes in paths, for training containers). |
| `dataset merge --org-id=<uuid> --name=<name> --dataset-ids=<id1>,<id2>` | Creates a new dataset containing the union of multiple source datasets. Source datasets remain unchanged. |
| `dataset data add ids --dataset-id=<uuid> --binary-data-ids=<ids>` | Associates specific binary data items with a dataset by ID (creates references, doesn't copy data). |
| `dataset data add filter --dataset-id=<uuid> [filter flags]` | Associates binary data matching a filter with a dataset. Parallelized with retries. |
| `dataset data remove ids --dataset-id=<uuid> --binary-data-ids=<ids>` | Removes binary data references from a dataset by ID. |
| `dataset data remove filter --dataset-id=<uuid> [filter flags]` | Removes binary data references from a dataset by filter. Automatically scopes the filter to only data in the specified dataset. |

### Examples

```bash
viam dataset create --org-id=abc123 --name=training-v2
viam dataset data add filter --dataset-id=ds123 --org-ids=abc123 --component-type=camera --tags=labeled
viam dataset export --dataset-id=ds123 --destination=./training-data --parallel=50
viam dataset merge --org-id=abc123 --name=combined --dataset-ids=ds1,ds2
viam dataset list --org-id=abc123
viam dataset delete --dataset-id=ds123
```

---

## 11. `datapipelines`

**Summary**: Manages serverless data transformation pipelines that run on a cron schedule. Each pipeline is defined by an MQL (MongoDB Query Language) aggregation pipeline that transforms data from a source collection.

**Implementation**: `cli/datapipelines.go`

### Subcommands

| Command | Description |
|---------|-------------|
| `datapipelines list --org-id=<uuid>` | Lists all pipelines for an org, showing name, ID, enabled status, and data source type. |
| `datapipelines create` | Creates a pipeline with a name, cron schedule, MQL query (inline JSON5 via `--mql` or from a file via `--mql-path`), data source type (`standard` or `hotstorage`), and optional backfill flag. |
| `datapipelines describe --id=<uuid>` | Shows full pipeline details: configuration, MQL query (pretty-printed), and the status/timing of the most recent run (scheduled, running, completed, or failed). |
| `datapipelines rename --id=<uuid> --name=<new-name>` | Renames a pipeline. |
| `datapipelines delete --id=<uuid>` | Deletes a pipeline. |
| `datapipelines enable --id=<uuid>` | Enables a pipeline (it will run on its cron schedule). |
| `datapipelines disable --id=<uuid>` | Disables a pipeline without deleting it. |

### Examples

```bash
viam datapipelines create --org-id=abc123 --name=daily-agg \
  --schedule="0 0 * * *" --data-source-type=standard \
  --mql='[{"$match":{"component_name":"camera-1"}},{"$out":"daily_summary"}]'

viam datapipelines create --org-id=abc123 --name=hourly-transform \
  --schedule="0 * * * *" --data-source-type=hotstorage \
  --mql-path=./pipeline-query.json

viam datapipelines describe --id=pipe123
viam datapipelines disable --id=pipe123
viam datapipelines list --org-id=abc123
```

---

## 12. `train`

**Summary**: Submits, monitors, and manages ML training jobs that run on Viam's cloud infrastructure.

**Implementation**: `cli/ml_training.go`

### Subcommands

| Command | Description |
|---------|-------------|
| `train submit managed` | Submits a training job using a Viam built-in training script. Specify `--dataset-id`, `--model-org-id`, `--model-name`, `--model-type` (single_label_classification, multi_label_classification, object_detection), `--model-framework` (tflite, tensorflow, pytorch, onnx), and `--model-labels`. |
| `train submit custom from-registry` | Submits a training job using a custom training script already in the registry. Identified by `--script-name=<org-id:script-name>`. Supports `--args` for passing key=value arguments to the script and `--container-version` for selecting the training container. |
| `train submit custom with-upload` | Uploads a training script and immediately submits a training job with it. The script gets registered as a side effect. Combines `training-script upload` + `train submit custom from-registry` in one step. |
| `train get --job-id=<uuid>` | Returns training job metadata (status, timestamps, model info). |
| `train logs --job-id=<uuid>` | Retrieves all training job log entries (paginated, fetches all pages). Each entry has a timestamp, level, and message. |
| `train cancel --job-id=<uuid>` | Sends a cancellation request for a running training job. |
| `train list --org-id=<uuid>` | Lists training jobs for an org. Optionally filter by `--job-status` (unspecified, pending, in_progress, completed, failed, canceled). |
| `train containers list` | Lists supported Docker container images for custom training. Shows name, framework, end-of-life date, and description. Pass `--include-uris` to include the container image URIs. |

### Examples

```bash
viam train submit managed --dataset-id=ds123 --model-org-id=abc123 \
  --model-name=my-detector --model-type=object_detection \
  --model-framework=tflite --model-labels=cat,dog

viam train submit custom from-registry --dataset-id=ds123 --org-id=abc123 \
  --script-name=my-org:my-trainer --version=1.0.0 \
  --model-name=custom-model --container-version=pytorch_gpu_1.13

viam train get --job-id=job123
viam train logs --job-id=job123
viam train list --org-id=abc123 --job-status=completed
viam train cancel --job-id=job123
viam train containers list --include-uris
```

---

## 13. `training-script`

**Summary**: Manages the training script packages that custom training jobs use. Training scripts are Python packages with `setup.py` and `model/training.py`, uploaded to Viam's registry as packages.

**Implementation**: `cli/ml_training.go`

### Subcommands

| Command | Description |
|---------|-------------|
| `training-script upload` | Packages and uploads a training script tarball to the registry. Sets metadata: `--model-type`, `--framework`, `--visibility` (public/private), `--draft` flag, and `--url`. |
| `training-script update` | Updates registry metadata for an existing script (visibility, description, URL) without re-uploading code. Validates that public scripts have a description. |
| `training-script test-local` | Runs a training script locally in a Docker container that mirrors the cloud training environment. Validates that `setup.py` and `model/training.py` exist. Mounts script directory, dataset, and output directory into the container. Uses Google Vertex AI containers (linux/x86_64 only; Rosetta emulation on ARM Macs). Supports `--custom-args` for passing key=value arguments. |

### Examples

```bash
viam training-script upload --path=./my-trainer.tar.gz --org-id=abc123 \
  --script-name=my-detector-trainer --version=1.0.0 \
  --framework=pytorch --model-type=object_detection --visibility=private

viam training-script update --org-id=abc123 --script-name=my-trainer \
  --visibility=public --description="Custom object detector"

viam training-script test-local \
  --training-script-directory=./my-trainer \
  --dataset-file=dataset.jsonl \
  --dataset-root=./data \
  --model-output-directory=./output \
  --container-version=pytorch_gpu_1.13 \
  --custom-args=epochs=10,learning_rate=0.001
```

---

## 14. `infer`

**Summary**: Runs cloud-hosted ML inference on a single binary data item (image). Sends the image to a model in the registry (supported frameworks: TFLite, TensorFlow, PyTorch, ONNX) and returns two kinds of results:

- **Output tensors** — The raw numerical output from the model. Each tensor has a name, a shape (dimensions), and an array of float values. For a classifier, this might be a single tensor of class probabilities. For a detector, there may be separate tensors for boxes, scores, and class indices. The tensor names and shapes depend on the model architecture.
- **Annotations** — Structured, human-readable results derived from the tensors. Bounding boxes include normalized coordinates (`[x_min, y_min, x_max, y_max]`), a label, and an optional confidence score. Classifications include a label and optional confidence.

**Implementation**: `cli/ml_inference.go`

### Flags

| Flag | Description |
|------|-------------|
| `--org-id` | Organization ID |
| `--binary-data-id` | ID of the binary data item to run inference on |
| `--model-org-id` | Organization ID of the model owner |
| `--model-name` | Name of the model in the registry |
| `--model-version` | Version of the model |

### Examples

```bash
viam infer --org-id=abc123 --binary-data-id=data456 \
  --model-org-id=abc123 --model-name=my-detector --model-version=1.0.0
```

---

## 15. `module`

**Summary**: Full lifecycle management for Viam modules: creating, scaffolding, building, uploading, downloading, and hot-reloading. Modules extend Viam with custom components and services.

**Implementation**: `cli/module_registry.go`, `cli/module_build.go`, `cli/module_generate.go`, `cli/module_reload.go`

### Registry Operations

| Command | Description |
|---------|-------------|
| `module create --name=<name>` | Registers a module on app.viam.com and creates a `meta.json` manifest file locally. Requires `--org-id` or `--public-namespace`. Pass `--local-only` to skip the API call and just generate the manifest. |
| `module generate` | Interactive scaffolding wizard. Prompts for language (Python/Go), resource subtype, model name, visibility, etc. Uses embedded templates to generate a complete module skeleton. Works unauthenticated (won't register with Viam). |
| `module update` | Pushes `meta.json` changes to the registry (description, models, visibility, entrypoint, apps, markdown docs). If the module ID uses an org ID and the org has a public namespace, auto-updates the manifest. |
| `module update-models --binary=<path>` | Runs the module binary in a sandbox, queries it for the API-model pairs it advertises, and updates `meta.json`. Also auto-detects markdown documentation files named `namespace_module_model.md`. |
| `module upload --version=<ver> --platform=<os/arch> <path>` | Uploads a module tarball for a specific version and platform. Validates the tarball: checks for an executable at the declared entrypoint, verifies file permissions, detects platform mismatches, warns about symlinks escaping the archive. Pass `--force` to skip validation. |
| `module download` | Downloads a module package from the registry. Specify `--id`, `--version` (or `latest`), `--platform`, and `--destination`. |
| `module restart` | Restarts a currently-running module on a remote machine part. |

### Build Operations

| Command | Description |
|---------|-------------|
| `module build local` | Runs the build command from `meta.json` locally. |
| `module build start --version=<ver>` | Triggers a cloud build. Can target multiple `--platforms`. Pass `--wait` to block until completion. |
| `module build list` | Shows cloud build status in a formatted table (job ID, platform, status, time). |
| `module build logs --build-id=<id>` | Retrieves logs from a specific cloud build job. |
| `module build link-repo --repo=<owner/repo>` | Links a GitHub repository to the module for automated CI builds. Initiates an OAuth flow. |

### Hot-Reload Operations

| Command | Description |
|---------|-------------|
| `module reload-local` | Builds the module locally (runs the `meta.json` build command), then deploys to a target machine. Adds a shell service if needed, uploads the built artifact, and configures the machine's module config to use `reload_path` for hot-reloading. |
| `module reload` | Builds the module in the cloud, then deploys to the target machine. Same configuration steps as `reload-local` but uses cloud builders. |
| `module local-app-testing` | Launches a local viam-server with a configuration file for testing module applications locally. |

### Examples

```bash
viam module create --name=my-sensor --org-id=abc123
viam module generate

viam module update --module=meta.json
viam module update-models --binary=./build/my-module

viam module upload --version=1.2.3 --platform=linux/amd64 ./dist/module.tar.gz
viam module download --id=my-org:my-module --version=latest --destination=./downloads

viam module build local
viam module build start --version=1.2.3 --platforms=linux/amd64,linux/arm64
viam module build list
viam module build logs --build-id=build123
viam module build link-repo --repo=my-org/my-module-repo

viam module reload --part=part123 --module=meta.json
viam module reload-local --part=part123 --module=meta.json

viam module restart --part=part123 --module=meta.json
```

---

## 16. `packages`

**Summary**: Low-level package upload/download against Viam's package registry. Modules, ML models, SLAM maps, and training scripts are all stored as typed packages.

**Implementation**: `cli/packages.go`

### Package Types

- `archive` — Generic archive
- `ml_model` — ML model (requires `--model-framework`)
- `module` — Viam module
- `slam_map` — SLAM map
- `ml_training` — ML training script (used internally by `training-script upload`)

### Subcommands

| Command | Description |
|---------|-------------|
| `packages upload --path=<file> --org-id=<uuid> --name=<name> --version=<ver> --type=<type>` | Uploads a tarball as a typed package. For `ml_model` type, `--model-framework` is required (tflite, tensorflow, pytorch, onnx). |
| `packages export --org-id=<uuid> --name=<name> --version=<ver> --type=<type> --destination=<dir>` | Downloads a package. If `--org-id` and `--name` are omitted, reads from `meta.json`. |

### Examples

```bash
viam packages upload --path=./model.tar.gz --org-id=abc123 \
  --name=my-model --version=1.0.0 --type=ml_model --model-framework=tflite

viam packages export --org-id=abc123 --name=my-model \
  --version=1.0.0 --type=ml_model --destination=./downloads
```

---

## 17. `metadata`

**Summary**: Reads arbitrary key-value metadata (JSON) attached to organizations, locations, machines, or machine parts. Metadata is a flexible store for custom attributes outside the standard schema.

**Implementation**: `cli/metadata_read.go`

### Subcommands

| Command | Description |
|---------|-------------|
| `metadata read` | Reads metadata. At least one of `--organization-id`, `--location-id`, `--machine-id`, `--machine-part-id` is required. If multiple are specified, metadata for each is displayed. |

### Examples

```bash
viam metadata read --organization-id=abc123
viam metadata read --machine-id=mach123 --machine-part-id=part456
```

---

## 18. `traces`

**Summary**: Works with OpenTelemetry trace data from viam-server. Each machine part writes trace spans to `~/.viam/trace/<part-id>/traces` in length-delimited protobuf format. This command lets you download, print, or forward those traces to an OTLP collector.

**Implementation**: `cli/traces.go`

### Subcommands

| Command | Description |
|---------|-------------|
| `traces import-local <path>` | Reads a local trace file and uploads all spans to an OTLP gRPC endpoint (`--endpoint`, defaults to `localhost:4317`). Adds TLS for non-localhost endpoints. |
| `traces import-remote --part=<id>` | Downloads traces from a remote machine via the shell service, then imports them to an OTLP endpoint. Combines `get-remote` + `import-local` in one step. |
| `traces print-local <path>` | Reads a local trace file and renders spans to the console in a human-readable development format with timing and hierarchy. |
| `traces print-remote --part=<id>` | Downloads traces from a remote machine and prints them locally. |
| `traces get-remote --part=<id> [target]` | Downloads all trace files (including rotated ones) from a remote machine to a local directory via the shell service. Defaults to the current directory if no target is specified. |

### Examples

```bash
viam traces print-local ./traces
viam traces print-remote --part=part123
viam traces get-remote --part=part123 ./my-traces/
viam traces import-local --endpoint=jaeger:4317 ./traces
viam traces import-remote --part=part123 --endpoint=jaeger:4317
```

---

## 19. `xacro`

**Summary**: Converts ROS xacro files to plain URDF for use with Viam's motion planning and kinematics.

Arm manufacturers (Universal Robots, xArm, Kinova, etc.) publish robot descriptions as xacro/URDF packages in the ROS ecosystem. Xacro files use macros, parameters, conditionals, and cross-package includes (`$(find package_name)`) that need expansion into a flat URDF before Viam can use them. This command handles that expansion by running `ros2 run xacro xacro` inside a Docker container with the appropriate ROS distribution. It auto-detects the ROS package from `package.xml` and discovers dependent packages in sibling directories.

Viam doesn't use ROS at runtime. This is a build-time conversion tool.

**Implementation**: `cli/xacro.go`

### What Viam Extracts from URDF

The generated URDF feeds into Viam's `referenceframe` package, which parses it into a kinematic model used for forward/inverse kinematics and collision-aware motion planning. Specifically:

- **Joints** — revolute, continuous, prismatic, and fixed. Each joint's axis, parent/child links, and limits define the kinematic chain. Unit conversion is automatic: URDF uses meters and radians; Viam converts to millimeters and degrees during parsing.
- **Collision geometry** — box, sphere, mesh (`.stl`/`.ply`), and capsule (cylinder + 2 spheres pattern) from `<collision>` elements. The motion planner uses these for self-collision and obstacle avoidance.
- **Mesh files** — `.stl` and `.ply` files referenced by `<mesh filename="..."/>` are loaded into memory. `package://` path prefixes are stripped automatically.
- **Ignored** — `<inertial>` (mass/inertia), `<visual>` geometry, `<transmission>`, Gazebo plugins. Viam doesn't simulate dynamics, so only kinematics and collision shapes matter.

### Using the Output in Viam

Common arms (UR5e, xArm6, etc.) already ship as pre-converted kinematic models embedded in the RDK binary — just set `arm_model: "ur5e"` in your machine config.

For custom or unsupported arms, convert the xacro to URDF, place the file on your machine, and reference it in your arm component config via `model_file_path`:

```json
{
  "type": "component",
  "model": "fake",
  "name": "my-arm",
  "attributes": {
    "model_file_path": "/path/to/my-robot.urdf"
  }
}
```

Viam parses the URDF at startup, builds a kinematic model, and registers it in the robot's frame system. The motion service then uses the model for planning, and the arm component uses it to compute end-effector poses from joint angles.

### Subcommands

| Command | Description |
|---------|-------------|
| `xacro convert` | Converts a xacro file to URDF. |

### Key Flags

| Flag | Description |
|------|-------------|
| `--input-file` | Path to the xacro file |
| `--output-file` | Path for the generated URDF |
| `--docker-image` | Docker image to use (default: `osrf/ros:humble-desktop`) |
| `--package-xml` | Path to `package.xml` (default: `./package.xml`) |
| `--collapse-fixed-joints` | Post-process: remove fixed joints where the child link is a leaf node. Use this when your URDF has tool flange chains (e.g., a UR5e's `wrist_3_link → ee_link → tool0`) that create multiple leaf nodes. Viam requires a single end effector, so collapsing these fixed branches gives a clean single-output kinematic chain. |
| `--install-packages` | Install `ros-<distro>-xacro` in the container before running. |
| `--ros-distro` | Override the ROS distribution (auto-detected from docker image tag, defaults to `humble`). |
| `--dry-run` | Print the Docker command without executing it. |
| `--args` | Pass xacro arguments (key:=value format). File path values are auto-converted to container paths. |

### Limitations

- **No SDF support** — only URDF. Gazebo's SDF format is not supported.
- **Single kinematic chain only** — Viam expects one end effector (one leaf node in the joint tree). Multi-arm or branching structures won't parse correctly.
- **No standalone cylinder collision geometry** — cylinders are only supported as part of a capsule pattern (1 cylinder + 2 spheres). Use box or sphere approximations otherwise.

### Examples

```bash
# Basic conversion with explicit Docker image
viam xacro convert --input-file=robot.xacro --output-file=robot.urdf \
  --docker-image=osrf/ros:humble-desktop

# Convert and clean up tool flange chains for Viam compatibility
viam xacro convert --input-file=robot.xacro --output-file=robot.urdf \
  --collapse-fixed-joints --install-packages

# Pass xacro arguments (e.g., parameterized robot model)
viam xacro convert --input-file=robot.xacro --output-file=robot.urdf \
  --args name:=ur20

# Preview the Docker command without running it
viam xacro convert --input-file=robot.xacro --output-file=robot.urdf \
  --args name:=ur20 --dry-run
```

---

## 20. `parse-ftdc`

**Summary**: Parses FTDC (Full-Time Diagnostic Data Capture) files and opens an interactive REPL for visualizing time-series performance data from viam-server.

**Implementation**: `cli/ftdc.go` (delegates to `ftdc/parser.LaunchREPL`)

### What FTDC Captures

Every running viam-server collects metrics once per second and writes them to compact binary files in `~/.viam/diagnostics.data/<part-id>/`. The data includes:

- **Process metrics** (`proc.viam-server`) — user/system CPU seconds, elapsed time, virtual memory (VSS), resident memory (RSS)
- **Network metrics** (`net`) — packets and bytes sent/received per interface, error counts
- **Web/WebRTC metrics** (`web`) — HTTP request counts, WebRTC peer connections, video/data bytes sent
- **Data sync metrics** (`data_manager`) — disk usage per sync path, files uploaded/pending, upload errors
- **Per-resource state** — every component and service in the resource graph reports its lifecycle state (ready, unconfigured, pending removal, error) and optional resource-specific stats
- **Module metrics** — modules can register custom statsers for their own metrics

Files rotate at ~10 MB, with a maximum of 20 files retained. The format uses delta compression (only changed values are written), so a typical week of data fits in a few megabytes.

### When to Use This

**Correlate CPU/memory with events** — A machine is sluggish at certain times. Open the FTDC data, mark the reported time with `ev`, and see which metrics spiked.

**Diagnose memory leaks** — Watch `RssMB` growth over time. Select it to pin it to the top of the graph.

**Investigate resource failures** — Per-resource state tracking shows when components entered error state and whether they recovered. Zoom in with `range` to see what else changed at the same time.

**Debug data sync issues** — Monitor upload rates vs. disk growth, detect disk-full conditions, watch for repeated upload errors.

**Profile module performance** — Per-module CPU and latency breakdowns show if a specific module is consuming disproportionate resources.

### Typical Workflow

1. Download FTDC data from a remote machine:
   ```bash
   viam machines part get-ftdc --part=<part-id> ./diagnostics/
   ```
2. Open the data in the REPL:
   ```bash
   viam parse-ftdc --path=./diagnostics/
   ```
3. The REPL generates `plot.png` with gnuplot — one subplot per metric, all sharing a time axis for correlation. Yellow lines mark file boundaries.

### REPL Commands

| Command | Description |
|---------|-------------|
| `help` / `h` | Show all commands |
| `range <start> <end>` | Filter to a time window. Use `start` or `end` as keywords for the beginning/end of the data. |
| `reset range` | Remove the time filter, show all data. |
| `event <timestamp>` / `ev <timestamp>` | Mark a point in time with a vertical blue line on the graph. Useful for correlating a reported incident with metric changes. |
| `select <metrics>` | Pin specific metrics to the top of the graph. Supports comma-separated names and regex (case-insensitive). |
| `deselect <metrics>` | Unpin metrics. `deselect all` clears all selections. |
| `show zeroes` | Include metrics that are all zeros in the graph (hidden by default). |
| `hide zeroes` | Hide all-zero metrics (default). |
| `quit` / Ctrl-D | Exit. |

The REPL auto-computes derived metrics: CPU percentages from cumulative seconds, per-second rates from counters, and latency averages.

### Examples

```bash
# Download FTDC from a remote machine, then explore locally
viam machines part get-ftdc --part=part123 ./diagnostics/
viam parse-ftdc --path=./diagnostics/

# Parse a specific FTDC file
viam parse-ftdc --path=./viam-server-2026-03-18T14-30-00Z.ftdc

# Parse all FTDC files in a directory (concatenated view)
viam parse-ftdc --path=~/.viam/diagnostics.data/my-part-id/
```

---

## 21. `version`

**Summary**: Prints the CLI version, build date, and git commit hash.

**Implementation**: `cli/client.go`

### Examples

```bash
viam version
```

---

## 22. `update`

**Summary**: Self-updates the `viam` CLI binary to the latest released version.

**Implementation**: `cli/client.go`

### Examples

```bash
viam update
```

---

## Implementation Files

| File | Scope |
|------|-------|
| `cli/app.go` | Command tree definitions, flag constants, argument parsing |
| `cli/auth.go` | Login, logout, whoami, API key creation, OAuth device code flow |
| `cli/client.go` | Organizations, locations, machines, version, update |
| `cli/data.go` | Data export, delete, tag, database configure |
| `cli/dataset.go` | Dataset CRUD, export, merge |
| `cli/datapipelines.go` | Data pipeline lifecycle |
| `cli/defaults.go` | Default org/location management |
| `cli/ftdc.go` | FTDC file parsing |
| `cli/metadata_read.go` | Metadata reading |
| `cli/ml_inference.go` | Cloud inference |
| `cli/ml_training.go` | Training jobs, training script upload/update/test |
| `cli/module_build.go` | Module build (local/cloud), build listing/logs, link-repo, reload, local-app-testing |
| `cli/module_generate.go` | Interactive module scaffolding |
| `cli/module_registry.go` | Module create, update, upload, download, update-models |
| `cli/module_reload.go` | Module reload configuration, resource/shell management |
| `cli/packages.go` | Package upload/export |
| `cli/profile.go` | CLI profile management |
| `cli/traces.go` | OpenTelemetry trace import/print/download |
| `cli/xacro.go` | Xacro-to-URDF conversion |
