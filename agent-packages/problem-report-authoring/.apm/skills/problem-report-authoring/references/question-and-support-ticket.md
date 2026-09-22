# The question, and the support ticket

Open this for two artifacts the bug form does not fit: a question to a project when you are not
sure the behavior is a defect, and a support ticket to a vendor or a hosted service whose source and
tracker you cannot see. Both keep the skill's evidence rules and its hand-over. The question opens
with the task you could not complete, as a request does; the ticket opens with what you did and what
you observed. What changes otherwise is the slots and the channel.

## The question: "is this a defect, or am I misusing it?"

File it where the project takes questions: a discussions board, a forum, a mailing list, a chat
channel, or the issue type the project names for questions. The routing lookup of step 2 finds the
place; a question filed as a bug is closed or moved, and a defect that was filed as a question is
moved the other way with your evidence intact, so the second mistake is the cheaper one.

The title does not say "bug". It names the task and what happened instead: "`retry` re-sends the
body after a timeout; is that intended?".

The slots, in order:

- **What you are trying to do**, in your own words, without the project's API.
- **What you did**, as steps with observable results, and the version.
- **What you read**, naming the page or the section, and what it led you to expect. This is the
  grounding question of §5 asked early, and it often answers the question before it is posted.
- **What happened instead**, pasted as text.
- **The question itself:** is this a defect, or a misuse, and if a misuse, what is the intended way to
  do the task.

What the question does not carry: a causal analysis of the project's code, a proposed fix, or an
expected-behavior block argued as a requirement. Where the answer is "a defect", the thread becomes
the source for a report under the rest of the skill, and it links back to the thread.

## The support ticket to a vendor

The vendor's form is the channel. There is no source to read, no template file, and no public
tracker to search; the status page, the known-issues page, and the vendor's documentation stand in
for the duplicate search and the grounding.

What replaces the skill's identifiers:

| The skill asks for | A ticket carries |
| --- | --- |
| The version | The account or tenant, the region, the service or plan name, and the timestamp of the observation with its timezone |
| The reproducer | The request and the response as the vendor's tooling shows them: request IDs, correlation IDs, a console URL, an API call with its exact response, a recording for a console defect |
| Ownership isolation | What you observed with one thing varied: another region, another account, another client, the vendor's own console against your client |
| The duplicate search | The status page and the known-issues page at the time of the observation, cited |
| The grounding | The vendor's documentation or the service level it publishes, cited by URL |

Severity is yours to set on a support form, unlike on a project's tracker, and it decides the
response time you get, so set it from the impact you observed and not from urgency you feel: the
form's own definitions of each level decide. Say what you want back, because the vendor cannot guess:
a workaround now, a root cause, a fix date, a credit, or a confirmation that the behavior is intended.

The rule of §6 applies in full, because the vendor is outside your organization and a ticket is
often forwarded further: secrets out, private names substituted. What stays is every identifier the
vendor needs to find the request or the resource: the account or tenant, the request and correlation
IDs, and the hostname, zone, bucket, or resource name on the vendor's platform, because the vendor
finds the resource by nothing else and a DNS or TLS failure can depend on the exact name. What is
substituted is what the vendor needs for nothing: the payload, your internal service and class
names, your users.

Where the ticket turns out to describe a defect in a product the vendor also ships as source, the
vendor's answer names the public tracker, and the report there is written under the rest of the
skill.
