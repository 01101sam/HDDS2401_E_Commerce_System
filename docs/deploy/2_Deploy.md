# Deploy codes to Azure

## Frontend

### Pre-requisites

1. Install [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli), do `az login` and `az upgrade` to
   ensure you have the latest version.

2. Install [Bun.SH](https://bun.SH). An engine that's faster and better than `Deno` and `Node.js`.

3. Your `deployment token` from [Obtain deployment token](1_Configure.md#obtain-deployment-token).

### Instructions

Open the terminal and navigate to the frontend directory.

Then, build and deploy the frontend to Azure.

```bash
bun run build
bunx swa deploy dist --deployment-token <token> --env production

# If you have set the environment variable
bun swa:deploy
```

`bun run build`

![img.png](img/step_2/img.png)
\
![img_1.png](img/step_2/img_1.png)

`bunx swa deploy dist --deployment-token <token> --env production`

![img_2.png](img/step_2/img_2.png)

## Backend

### Pre-requisites

1. Install [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli), do `az login` and `az upgrade` to
   ensure you have the latest version.

2. Install [Azure Functions Core Tools](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=linux%2Ccsharp%2Cbash#v2).

3. (Optional) Install Docker Desktop for later use.

> If you want to deploy via remote build, you can skip this step.

| OS      | Link                                                           |
|---------|----------------------------------------------------------------|
| Windows | https://docs.docker.com/desktop/setup/install/windows-install/ |
| MacOS   | https://docs.docker.com/desktop/setup/install/mac-install/     |
| Linux   | https://docs.docker.com/desktop/setup/install/linux/           |

### Instructions

Open the terminal and navigate to the backend directory.

Then, build and deploy the backend to Azure.

> **Note**
> 
> It's normal to see `FunctionHostSyncTrigger, statusCode = Unauthorized` error.
> \
> This is because the function app already linked to frontend and not accepting direct requests.

```bash
# Remote
func azure functionapp publish backend-api

# Local (Make sure Docker Desktop is installed)
func azure functionapp publish backend-api --build-native-deps -b local
```

#### Remote

![img_3.png](img/step_2/img_3.png)

#### Local

> **Note**
> 
> If you deploy the first time and see `ServiceUnavailable` error. Please try again.
> ![img_4.png](img/step_2/img_4.png)

![img_5.png](img/step_2/img_5.png)

# Testing

## Frontend

Enter the frontend URL in the browser.

![img.png](img/step_2/img_6.png)

## Backend

Enter the frontend URL + `/api/docs` to access API documentation.

![img_1.png](img/step_2/img_7.png)

### Register a dummy account

![img.png](img/step_2/img_8.png)
\
![img_1.png](img/step_2/img_9.png)

### Login

![img_2.png](img/step_2/img_10.png)
\
![img_3.png](img/step_2/img_11.png)

### Verify in Azure Portal

Go to `mdb` -> `Data Explorer`.

Select `user` -> `Documents`.

![img_4.png](img/step_2/img_12.png)

### Upload media

Go back to api docs and register an admin account using your own email and password.

Then, add role `admin`

![img_5.png](img/step_2/img_13.png)

When done, click `Update`

Now login, and save your access token.

Open [Postman](https://www.postman.com/downloads/), download if you haven't.

Create a new request, set the method to `POST`, and enter the URL.

Go to tab `Authorization`, select `Bearer Token`, and paste the access token.

![img_6.png](img/step_2/img_14.png)

Go to tab `Body`, select `form-data`, and enter the key as `file` and select a file.

![img_7.png](img/step_2/img_15.png)

You should see your response.

![img_8.png](img/step_2/img_16.png)

Click on the path, and copy your authorization token to new reqeust.

![img_9.png](img/step_2/img_17.png)
