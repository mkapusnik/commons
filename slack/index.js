const { IncomingWebhook } = require('@slack/webhook');
const webhook = new IncomingWebhook(process.env.SLACK_WEBHOOK);

module.exports.subscribe = (event) => {
    const build = eventToBuild(event.data);
    const status = [
        'SUCCESS',
        'FAILURE',
        'INTERNAL_ERROR',
        'TIMEOUT',
    ];
    if (status.indexOf(build.status) === -1) return;

    let branch = build.substitutions.BRANCH_NAME;
    if (!branch) return;
    const message = createSlackMessage(build);
    (async () => { await webhook.send(message); })();
};

const eventToBuild = (data) => {
    return JSON.parse(Buffer.from(data, 'base64').toString());
};

const createSlackMessage = (build) => {
    let buildCommit = build.substitutions.COMMIT_SHA || '';
    let branch = build.substitutions.BRANCH_NAME || '';
    let repoName = 'BuildMonitor'; //build.source.repoSource.repoName.split('_').pop() || ''; //Get repository name

    let color;
    switch (build.status) {
        case 'SUCCESS': color = "good"; break;
        case 'FAILURE': case 'INTERNAL_ERROR': case 'TIMEOUT': color = "danger"; break;
        default: color = "warning";
    }

    return {
        username: repoName,
        attachments: [
            {
                color: color,
                fields: [
                    {
                        title: "Branch",
                        value: branch,
                        short: true
                    },
                    {
                        title: "Status",
                        value: build.status,
                        short: true
                    }
                ],
                actions: [
                    {
                        text: 'View Logs',
                        type: 'button',
                        url: build.logUrl
                    },
                    {
                        text: 'View Commit',
                        type: 'button',
                        url: `https://github.com/mkapusnik/${repoName}/commit/${buildCommit}`
                    },
                ],
            },
        ],
    };
};