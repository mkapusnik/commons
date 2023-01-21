
    gcloud functions deploy slack
    --entry-point subscribe
    --stage-bucket commons_functions
    --trigger-topic cloud-builds
    --set-env-vars SLACK_WEBHOOK=https://hooks.slack.com/services/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
    --project cloud-build-monitor
    --runtime nodejs16
    --region europe-west3