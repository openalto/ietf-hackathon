## QoS tracking code of FTS 

In FTS, job and file state machines are depicted [here](https://fts3-docs.web.cern.ch/fts3-docs/docs/state_machine.html). A single file is failed if *"FAILED Transfer failed, and the retries have been exhausted"*. 

Upadtes in transmission rates (with optimization as represented in the docs with the optimization algorithm [here](https://fts3-docs.web.cern.ch/fts3-docs/docs/optimizer/optimizer.html)) mainly is done in [OptimizerConnections](https://gitlab.cern.ch/fts/fts3/-/blob/develop/src/server/services/optimizer/OptimizerConnections.cpp#L160) file. The optimizeConnectionsForPair function fetches the success rate form db. All db operations are handled using MySQL. The function which is called to fetch the success rate is [getSuccessRateForPair](https://gitlab.cern.ch/fts/fts3/-/blob/develop/src/db/mysql/OptimizerDataSource.cpp#L285). 

getSuccessRateForPair function aggregates all the files which belongs to a single transmission and counts the number of failed and finished files accordingly. 

States of the jobs and transfers/files are updated by the QoS-daemon or the transfer service. In the QoS daemon, contexts are responsible for tracking the states of different jobs. While tasks are updating the states for different states inside contexts. Detailed documentation of the QoS-daemon is [here](https://fts3-docs.web.cern.ch/fts3-docs/docs/qos-service/qos-service.html). 

`Different tasks are documented in the above link.`

ctx.cdmiUpdateFileStateToFailed function change the state of a file to failed. This function is called in [this file](https://gitlab.cern.ch/fts/fts3/-/blob/develop/src/qos-daemon/task/CDMIPollTask.cpp#L61) due to three mains reasons. 

1. Transition has finished but did not reach target QoS.
2. Target QoS has changed to a different value.
3. **Poll check exceeded the maximum retry limit.** *Seems to be the main reason*

**Note that** The Service is also able to ignore bringonline polling errors up to a configurable number (3 by default). **This prevents failing long lasting requests due to temporary network or storage glitches.** (I beleive that this 

**Finally**, staging state updater object of the [CDMIQosTransitionContext](https://gitlab.cern.ch/fts/fts3/-/blob/develop/src/qos-daemon/context/CDMIQosTransitionContext.h#L38) class updates the db which is used to calculate the success rate using [StagingStateUpdater](https://gitlab.cern.ch/fts/fts3/-/blob/develop/src/qos-daemon/state/StagingStateUpdater.h#L84).

Besides files, other tasks based contexts are also changeable to the Failed state, **they are not used in the optimization algorithm though.** Each job type inherits ctx.updateState and calls it with a proper failure reason. 

A list of Failed files and their respective complete logs are available [here](https://fts3-pilot.cern.ch:8449/fts3/ftsmon/#/transfers?state=FAILED&vo=escape&source_se=davs:%2F%2Fdclxwp2dlds1.gsi.de&dest_se=davs:%2F%2Fccdcalitest10.in2p3.fr&reason=SOURCE%20%5B113%5D%20Result%20Domain%20name%20resolution%20failed%20after%201%20attempts&time_window=1).
## Conclusion 





