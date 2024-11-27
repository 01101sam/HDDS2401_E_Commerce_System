# Config resources

In this section, we will link the resources we created in the previous steps.

> **Note**
>
> Free plan is lack of most features, please use standard plan.

## Storage Account

### Obtain connection string

From `ecommedia`, go to `Settings` -> `Access keys`

![img_5.png](img/step_1/img_5.png)

Note down `Connection string` from `key1`, we will use it later.

### Create container

Go to `Data storage` -> `Containers`

![img_3.png](img/step_1/img_3.png)

Click `+ Container`

Type `images`

![img_4.png](img/step_1/img_4.png)

## Frontend

### Obtain deployment token

From `front`, click `Manage deployment token` in tabs.

![img_2.png](img/step_1/img_2.png)

Note down deployment token, we will use it later.

### Linking Backend

From `front`, go to `Settigns` -> `APIs`

![img.png](img/step_1/img.png)

Click `Link` on field `Production`

![img_1.png](img/step_1/img_1.png)

Now you're done linking and backend will only be able to access via frontend's `/api` path.

This ensures that the backend is only accessible via the frontend by `vnet`.

## Database

Wait until the database is deployed.

### Obtain connection string

From `mdb`, go to `Settings` -> `Connection string`

![img_6.png](img/step_1/img_6.png)

Note down `Primary connection string`, we will use it later.

### Create collection

Go to `Data Explorer` -> `New Collection`

![img_7.png](img/step_1/img_7.png)

- **Database id**: `ecom_db`
- **Collection id**: `user`
- **Sharding**: `Unsharded (20GB limit)`

### Enable connection for Azure portal middleware

Go to `Networking` (From `Settings`)

![img_8.png](img/step_1/img_8.png)

Click `+ Add Azure Portal Middleware IPs`

Then click `Save`

This step ensures you can update your role from Azure portal later.

## Backend (Function App)

From `backend-api`, go to `Settings` -> `Environment variables`

![img_9.png](img/step_1/img_9.png)

You may see `.env.example.json` from the repository,
\
copy the content and follow the instructions in `.env.example` to fill in the values.

After done, open `Advanced edit` and paste the content.
\
Reminder: Don't overwrite the existing content!

![img_10.png](img/step_1/img_10.png)

Click `OK`, then `Apply`

And `Confirm`.
