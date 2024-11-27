# Setup

We will use the following resources:

| Resource         | Link                                                                     |
|------------------|--------------------------------------------------------------------------|
| Resource groups  | https://portal.azure.com/#browse/resourcegroups                          |
| Virtual networks | https://portal.azure.com/#browse/Microsoft.Network%2FvirtualNetworks     |
| Storage accounts | https://portal.azure.com/#browse/Microsoft.Storage%2FStorageAccounts     |
| Azure Cosmos DB  | https://portal.azure.com/#browse/Microsoft.DocumentDb%2FdatabaseAccounts |
| Function App     | https://portal.azure.com/#browse/Microsoft.Web%2Fsites/kind/functionapp  |
| Static Web Apps  | https://portal.azure.com/#browse/Microsoft.Web%2FStaticSites             |

Recommend to open all the links in a new tab since they need time to deploy.
\
While one resources are deploying, you can start moving to the next one. (expect for `Resource groups` and
`Virtual networks`)

Recommend region: `East Asia`

## Resource Group

![img.png](img/step_0/img.png)

- **Resource group name**: any name you want, in this tutorial will use `ecom_res_group`
- **Region**: `East Asia`

Then sentence `any name you want, in this tutorial will use` will not be shown later on
\
unless specified for other reason.

This also applies on field `Region`.

## Virtual Network

![img_1.png](img/step_0/img_1.png)
\
![img_2.png](img/step_0/img_2.png)

- **Virtual network name**: `vnet`
- Tab **IP Addresses**: using default values

Deploy may need some time, but you can already start deploying the next resource.

## Storage Account

![img_3.png](img/step_0/img_3.png)

- **Storage account name**: `ecommedia`
- **Redundancy**: `Locally-redundant storage (LRS)`

![img_4.png](img/step_0/img_4.png)

- **Network connectivity**: `Disable network access and use private access`

Click `+ Add private endpoint`

![img_5.png](img/step_0/img_5.png)

- **Private endpoint name**: `media-priv-link`
- **Virtual network**: `vnet`
    - **Subnet**: `default`

Deploy need a few minutes, please move on.

## Azure Cosmos DB

![img_6.png](img/step_0/img_6.png)

- **Which API best suits your workload?**: `Azure Cosmos DB for MongoDB`

![img_7.png](img/step_0/img_7.png)

- **Resource**: `Request unit (RU) database account`

![img_8.png](img/step_0/img_8.png)

- **Account name**: `mdb`
- **Capacity mode**: `Serverless`

![img_9.png](img/step_0/img_9.png)

- **Allow Public Network Access**: `Deny`

At `Private endpoint`, Click `+ Add`

![img_10.png](img/step_0/img_10.png)

Deploy need a few minutes, please move on.

## Function App

![img_11.png](img/step_0/img_11.png)

- **Hosting plans**: `Flex Consumption`

![img_12.png](img/step_0/img_12.png)

- **Function App name**: `backend-api` (*-XXXXX.eastasia-01.azurewebsites.net*)
- **Secure unique default hostname (preview) on.**: `Yes`
- **Runtime stack**: `Python`
- **Version**: `3.11`
- **Instance size**: `2048 MB`

![img_13.png](img/step_0/img_13.png)

- **Storage account**: `backendfuncapp`

![img_14.png](img/step_0/img_14.png)

- **Enable network injection**: `Yes`
- **Virtual network**: `vnet`

![img_15.png](img/step_0/img_15.png)

Create a new subnet

![img_16.png](img/step_0/img_16.png)

- **Subnet Name**: `backend-api-sn`

Deploy need a few minutes, please move on.

## Static Web Apps

![img_17.png](img/step_0/img_17.png)

- **Name**: `front`
- **Source**: `Other` (Will will upload via local deployment)

![img_18.png](img/step_0/img_18.png)

- **Distributed Functions (preview)**: `Yes`

## Summary

Now for all resources that's deploy completed, please click `Go to resource` to go inside the resource.

- **Resource group**: `ecom_res_group`
- **Virtual network**: `vnet`
- **Storage account**: `ecommedia`
- **Azure Cosmos DB**: `mdb`
- **Function App**: `backend-api`
- **Static Web Apps**: `front`

Now you have all the resources deployed (exclude `mdb`), you can start configuring them.

For database, you may need up to 5 minutes (and more) to deploy.

But you can still move on as there's something you can configure.
