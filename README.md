****[![Downloads](https://static.pepy.tech/badge/python-amazon-sp-api)](https://pepy.tech/project/python-amazon-sp-api)
[![Downloads](https://static.pepy.tech/badge/python-amazon-sp-api/month)](https://pepy.tech/project/python-amazon-sp-api)
[![Downloads](https://static.pepy.tech/badge/python-amazon-sp-api/week)](https://pepy.tech/project/python-amazon-sp-api)

# PYTHON-AMAZON-SP-API

## Amazon Selling-Partner API

A wrapper to access **Amazon's Selling Partner API** with an easy-to-use interface.


---

# 🌟 Thank you for using python-amazon-sp-api! 🌟

This tool helps developers and businesses connect seamlessly with Amazon's vast marketplace, enabling powerful automations and data management.

If you appreciate this project and find it useful, please consider supporting its continued development:

- 🙌 [GitHub Sponsors](https://github.com/sponsors/saleweaver)
- 🌐 BTC Address: `bc1q6uqgczasmnvnc5upumarugw2mksnwneg0f65ws`
- 🌐 ETH Address: `0xf59534F7a7F5410DBCD0c779Ac3bB6503bd32Ae5`

Your support helps keep the project alive and evolving, and is greatly appreciated!

## Additional tools are available for sponsors.

All `$10/month+` sponsors get access to the `python-amazon-sp-api-tools` repository, which will contain additional tools and scripts to help you get the most out of the Amazon Selling Partner API.
Save $$$ on your Amazon Selling Partner API integration by becoming a sponsor today!

![GitHub Sponsors](https://img.shields.io/github/sponsors/saleweaver?logo=GitHub&color=lightgray)

----

### Documentation

Documentation is available [here](https://python-amazon-sp-api.readthedocs.io/en/latest/)

[![Documentation Status](https://img.shields.io/readthedocs/python-amazon-sp-api?style=for-the-badge)](https://python-amazon-sp-api.readthedocs.io/en/latest/index.html)


### Q & A

If you have questions, please ask them in GitHub discussions 

[![discussions](https://img.shields.io/badge/github-discussions-brightgreen?style=for-the-badge&logo=github)](https://github.com/saleweaver/python-amazon-sp-api/discussions)

or

[![join on slack](https://img.shields.io/badge/slack-join%20on%20slack-orange?style=for-the-badge&logo=slack)](https://join.slack.com/t/sellingpartnerapi/shared_invite/zt-zovn6tch-810j9dBPQtJsvw7lEXSuaQ)


### Installation
[![Badge](https://img.shields.io/pypi/v/python-amazon-sp-api?style=for-the-badge)](https://pypi.org/project/python-amazon-sp-api/)
```
pip install python-amazon-sp-api
pip install "python-amazon-sp-api[aws]" # if you want to use AWS Secret Manager Authentication.
pip install "python-amazon-sp-api[aws-caching]" # if you want to use the Cached Secrets from AWS
```

---
### Usage

```python
from sp_api.api import Orders
from sp_api.api import Reports
from sp_api.api import DataKiosk
from sp_api.api import Feeds
from sp_api.base import SellingApiException
from sp_api.base.reportTypes import ReportType
from datetime import datetime, timedelta

# DATA KIOSK API
client = DataKiosk()

res = client.create_query(query="{analytics_salesAndTraffic_2023_11_15{salesAndTrafficByAsin(startDate:\"2022-09-01\" endDate:\"2022-09-30\" aggregateBy:SKU marketplaceIds:[\"ATVPDKIKX0DER\"]){childAsin endDate marketplaceId parentAsin sales{orderedProductSales{amount currencyCode}totalOrderItems totalOrderItemsB2B}sku startDate traffic{browserPageViews browserPageViewsB2B browserPageViewsPercentage browserPageViewsPercentageB2B browserSessionPercentage unitSessionPercentageB2B unitSessionPercentage}}}}")
print(res)

# orders API
try:
    res = Orders().get_orders(CreatedAfter=(datetime.utcnow() - timedelta(days=7)).isoformat())
    print(res.payload)  # json data
except SellingApiException as ex:
    print(ex)


# report request     
create_report_response = Reports().create_report(reportType=ReportType.GET_MERCHANT_LISTINGS_ALL_DATA)

# submit feed
# feeds can be submitted like explained in Amazon's docs, or simply by calling submit_feed

Feeds().submit_feed(<feed_type>, <file_or_bytes_io>, content_type='text/tsv', **kwargs)

# PII Data

Orders(restricted_data_token='<token>').get_orders(CreatedAfter=(datetime.utcnow() - timedelta(days=7)).isoformat())

# or use the shortcut
orders = Orders().get_orders(
    LastUpdatedAfter=(datetime.utcnow() - timedelta(days=1)).isoformat()
)
```

---


### New endpoints

You can create a new endpoint file by running `make_endpoint <model_json_url>`

```bash
make_endpoint https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/models/listings-restrictions-api-model/listingsRestrictions_2021-08-01.json
```

This creates a ready to use client. Please consider creating a pull request with the new code.


### ADVERTISING API

You can use nearly the same client for the Amazon Advertising API. [@denisneuf](https://github.com/denisneuf) has built [Python-Amazon-Advertising-API](https://github.com/denisneuf/python-amazon-ad-api) on top of this client.
Check it out [here](https://github.com/denisneuf/python-amazon-ad-api)

### DISCLAIMER

We are not affiliated with Amazon


### LICENSE

![License](https://img.shields.io/github/license/saleweaver/python-amazon-sp-api?style=for-the-badge)

---

### Base Client

The client is pretty extensible and can be used for any other API. Check it out here:

[API Client](https://github.com/saleweaver/rapid_rest_client)

---

### Polling Manager

We have introduced a new module called `polling_manager` to handle pagination and backoff strategies automatically. This makes it easier to fetch all records without worrying about pagination limits or implementing exponential backoff.

#### Vanilla Method

Previously, to get orders, you would use the `Orders` module like this:

```python
from sp_api.api import Orders

orders_client = Orders(
    credentials=credentials,
    marketplace=Marketplaces.US
)


orders = orders_client.get_orders(
        CreatedAfter=one_week_ago
)
```

This method does not handle pagination and backoff, so if you have more than 100 records, you won't be able to get all your records.

#### Using Polling Manager

With the new polling_manager module, you can fetch all orders easily:

```python
from sp_api.polling_manager import PollingManager

pm = PollingManager(
    marketplace=Marketplaces.US,
    credentials=credentials,
)

orders = pm.orders.fetch_all_orders(
    CreatedAfter=one_week_ago
)
```

The polling_manager automatically handles pagination and backoff strategy for you, ensuring that the final result is complete even if you have more than 100 records. You don't have to worry about implementing exponential backoff.

The parameters are the same as the vanilla method, so you can use the same parameters to filter your results.

---

For now, the `polling_manager` module is only available for the `Orders` module. We will be adding support for other modules soon.

Supported methods:
    
```python
polling_manager.orders.fetch_all_orders()
polling_manager.orders.fetch_all_order_items()
polling_manager.orders.fetch_all_order_addresses()
```