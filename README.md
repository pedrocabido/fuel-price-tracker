# fuel-price-tracker

This project's goal is to alert users about expected fuel price changes in Portugal for next week by sending automated messages to [this](https://t.me/fuel_price_alert_pt) Telegram public channel.

We gather information from [this](https://contaspoupanca.pt/) source from a post like [this](https://contaspoupanca.pt/2024/04/26/combustiveis-precos-na-proxima-semana-29-de-abril-a-5-de-maio/).

This project is using Python and AWS Lambda with AWS EventBridge for cron triggering.

We also use [Chalice](https://github.com/aws/chalice) to deploy the application.

## How to use?

On the root of the project run the following command to deploy the application:

```shell
chalice deploy
```

Make sure to configure AWS credentials on `~/.aws/credentials`.
