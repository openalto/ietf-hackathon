#   Copyright  Members of the EMI Collaboration, 2013.
#   Copyright 2020 CERN
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from datetime import timedelta
import json
import sys
import time

from .base import Base
from fts3.rest.client import Submitter, Delegator, Inquirer

DEFAULT_PARAMS = {
    "checksum": "ADLER32",
    "overwrite": False,
    "overwrite_on_retry": False,
    "overwrite_hop": False,
    "reuse": False,
    "job_metadata": None,
    "file_metadata": None,
    "staging_metadata": None,
    "filesize": None,
    "gridftp": None,
    "spacetoken": None,
    "source_spacetoken": None,
    "verify_checksum": "n",
    "copy_pin_lifetime": -1,
    "bring_online": -1,
    "dst_file_report": False,
    "archive_timeout": -1,
    "timeout": None,
    "fail_nearline": False,
    "retry": 0,
    "multihop": False,
    "credential": None,
    "nostreams": None,
    "s3alternate": False,
    "target_qos": None,
    "ipv4": False,
    "ipv6": False,
    "buffer_size": None,
    "strict_copy": False,
}


def _metadata(data):
    if data is None:
        return None
    if isinstance(data, dict):
        return data
    try:
        return json.loads(data)
    except Exception:
        return str(data)


class JobSubmitter(Base):
    def __init__(self):
        super(JobSubmitter, self).__init__(
            extra_args="SOURCE DESTINATION [CHECKSUM]",
            description="""
            This command can be used to submit new jobs to FTS3. It supports simple and bulk submissions. The bulk
            format is as follows:

            ```json
            {
              "files": [
                {
                  "sources": [
                    "gsiftp://source.host/file"
                  ],
                  "destinations": [
                    "gsiftp://destination.host/file"
                  ],
                  "metadata": "file-metadata",
                  "checksum": "ADLER32:1234",
                  "filesize": 1024
                },
                {
                  "sources": [
                    "gsiftp://source.host/file2"
                  ],
                  "destinations": [
                    "gsiftp://destination.host/file2"
                  ],
                  "metadata": "file2-metadata",
                  "checksum": "ADLER32:4321",
                  "filesize": 2048,
                  "activity": "default"
                }
              ]
            }
            ```
            """,
            example="""
            $ %(prog)s -s https://fts3-devel.cern.ch:8446 gsiftp://source.host/file gsiftp://destination.host/file
            Job successfully submitted.
            Job id: 9fee8c1e-c46d-11e3-8299-02163e00a17a

            $ %(prog)s -s https://fts3-devel.cern.ch:8446 -f bulk.json
            Job successfully submitted.
            Job id: 9fee8c1e-c46d-11e3-8299-02163e00a17a
            """,
        )

        # Specific options
        self.opt_parser.add_option(
            "-b",
            "--blocking",
            dest="blocking",
            default=False,
            action="store_true",
            help="blocking mode. Wait until the operation completes.",
        )
        self.opt_parser.add_option(
            "-i",
            "--interval",
            dest="poll_interval",
            type="int",
            default=30,
            help="interval between two poll operations in blocking mode.",
        )
        self.opt_parser.add_option(
            "-e",
            "--expire",
            dest="proxy_lifetime",
            type="int",
            default=420,
            help="expiration time of the delegation in minutes.",
        )
        self.opt_parser.add_option(
            "--delegate-when-lifetime-lt",
            type=int,
            default=120,
            help="delegate the proxy when the remote lifetime is less than this value (in minutes)",
        )
        self.opt_parser.add_option(
            "-o",
            "--overwrite",
            dest="overwrite",
            action="store_true",
            help="overwrite files.",
        )
        self.opt_parser.add_option(
            "--overwrite-on-retry",
            dest="overwrite_on_retry",
            action="store_true",
            help="overwrite files on retries.",
        )
        self.opt_parser.add_option(
            "--overwrite-hop",
            dest="overwrite_hop",
            action="store_true",
            help="overwrite all files except the destination in a multihop submission.",
        )
        self.opt_parser.add_option(
            "-r",
            "--reuse",
            dest="reuse",
            action="store_true",
            help="enable session reuse for the transfer job.",
        )
        self.opt_parser.add_option(
            "--job-metadata", dest="job_metadata", help="transfer job metadata."
        )
        self.opt_parser.add_option(
            "--file-metadata", dest="file_metadata", help="file metadata."
        )
        self.opt_parser.add_option(
            "--staging-metadata", dest="staging_metadata", help="staging metadata."
        )
        self.opt_parser.add_option(
            "--file-size", dest="file_size", type="long", help="file size (in Bytes)"
        )
        self.opt_parser.add_option(
            "-g", "--gparam", dest="gridftp_params", help="GridFTP parameters."
        )
        self.opt_parser.add_option(
            "-t",
            "--dest-token",
            dest="destination_token",
            help="the destination space token or its description.",
        )
        self.opt_parser.add_option(
            "-S",
            "--source-token",
            dest="source_token",
            help="the source space token or its description.",
        )
        self.opt_parser.add_option(
            "-K",
            "--compare-checksum",
            dest="compare_checksum",
            default=False,
            action="store_true",
            help="deprecated: compare checksums between source and destination.",
        )
        self.opt_parser.add_option(
            "-C",
            "--checksum-mode",
            dest="checksum_mode",
            type="string",
            help="compare checksums in source, target, both or none.",
        )
        self.opt_parser.add_option(
            "--copy-pin-lifetime",
            dest="pin_lifetime",
            type="long",
            help="pin lifetime of the copy in seconds.",
        )
        self.opt_parser.add_option(
            "--bring-online",
            dest="bring_online",
            type="long",
            help="bring online timeout in seconds.",
        )
        self.opt_parser.add_option(
            "--dst-file-report",
            dest="dst_file_report",
            action="store_true",
            help="report on the destination tape file if it already exists and overwrite is off.",
        )
        self.opt_parser.add_option(
            "--archive-timeout",
            dest="archive_timeout",
            type="long",
            help="archive timeout in seconds.",
        )
        self.opt_parser.add_option(
            "--timeout",
            dest="timeout",
            type="long",
            help="transfer timeout in seconds.",
        )
        self.opt_parser.add_option(
            "--fail-nearline",
            dest="fail_nearline",
            action="store_true",
            help="fail the transfer is the file is nearline.",
        )
        self.opt_parser.add_option(
            "--dry-run",
            dest="dry_run",
            default=False,
            action="store_true",
            help="do not send anything, just print the JSON message.",
        )
        self.opt_parser.add_option(
            "-f",
            "--file",
            dest="bulk_file",
            type="string",
            help="Name of configuration file",
        )
        self.opt_parser.add_option(
            "--retry",
            dest="retry",
            type="int",
            help="Number of retries. If 0, the server default will be used."
            "If negative, there will be no retries.",
        )
        self.opt_parser.add_option(
            "-m",
            "--multi-hop",
            dest="multihop",
            action="store_true",
            help="submit a multihop transfer.",
        )
        self.opt_parser.add_option(
            "--cloud-credentials",
            dest="cloud_cred",
            help="use cloud credentials for the job (i.e. dropbox).",
        )
        self.opt_parser.add_option(
            "--nostreams", dest="nostreams", help="number of streams"
        )
        self.opt_parser.add_option(
            "--ipv4", dest="ipv4", action="store_true", help="force ipv4"
        )
        self.opt_parser.add_option(
            "--ipv6", dest="ipv6", action="store_true", help="force ipv6"
        )
        self.opt_parser.add_option(
            "--s3alternate",
            dest="s3alternate",
            action="store_true",
            help="use S3 alternate URL",
        )
        self.opt_parser.add_option(
            "--target-qos",
            dest="target_qos",
            type="string",
            help="define the target QoS for this transfer for CDMI endpoints",
        )
        self.opt_parser.add_option(
            "--buffer-size",
            "--buff-size",
            dest="buffer_size",
            type=int,
            help="TCP buffer size (expressed in bytes) that will be used for the given transfer job",
        )
        self.opt_parser.add_option(
            "--strict-copy",
            dest="strict_copy",
            action="store_true",
            help="disable all checks, just copy the file",
        )

    def validate(self):
        self.checksum = None
        if not self.options.bulk_file:
            if len(self.args) < 2:
                self.logger.critical("Need a source and a destination")
                sys.exit(1)
            elif len(self.args) == 2:
                (self.source, self.destination) = self.args
            elif len(self.args) == 3:
                (self.source, self.destination, self.checksum) = self.args
            else:
                self.logger.critical("Too many parameters")
                sys.exit(1)

        self._prepare_options()
        if self.params["ipv4"] and self.params["ipv6"]:
            self.opt_parser.error("ipv4 and ipv6 can not be used at the same time")
        if (
            sum(
                [
                    self.params["overwrite"],
                    self.params["overwrite_on_retry"],
                    self.params["overwrite_hop"],
                ]
            )
            > 1
        ):
            self.opt_parser.error(
                "Multiple overwrite flags can not be used at the same time"
            )

    def _build_transfers(self):
        if self.options.bulk_file:
            with open(self.options.bulk_file, "r") as file:
                filecontent = file.read()
                bulk = json.loads(filecontent)
            if "files" in bulk:
                return bulk["files"]
            elif "Files" in bulk:
                return bulk["Files"]
            else:
                self.logger.critical("Could not find any transfers")
                sys.exit(1)
        else:
            return [{"sources": [self.source], "destinations": [self.destination]}]

    def _build_params(self, **kwargs):
        params = dict()
        params.update(DEFAULT_PARAMS)

        if self.options.bulk_file:
            with open(self.options.bulk_file, "r") as file:
                filecontent = file.read()
                bulk = json.loads(filecontent)
            if "params" in bulk:
                params.update(bulk["params"])

        # Apply command-line parameters
        for k, v in kwargs.items():
            if v is not None:
                params[k] = v

        # JSONify metadata
        params["job_metadata"] = _metadata(params["job_metadata"])
        params["file_metadata"] = _metadata(params["file_metadata"])
        params["staging_metadata"] = _metadata(params["staging_metadata"])
        return params

    def _prepare_options(self):
        # Backwards compatibility: compare_checksum parameter
        # Note: compare_checksum has higher priority than checksum_mode
        if self.options.compare_checksum:
            checksum_mode = "both"
        elif self.options.checksum_mode:
            checksum_mode = self.options.checksum_mode
        else:
            checksum_mode = "none"

        self.transfers = self._build_transfers()
        self.params = self._build_params(
            checksum=self.checksum,
            bring_online=self.options.bring_online,
            dst_file_report=self.options.dst_file_report,
            archive_timeout=self.options.archive_timeout,
            timeout=self.options.timeout,
            verify_checksum=checksum_mode[0],
            spacetoken=self.options.destination_token,
            source_spacetoken=self.options.source_token,
            fail_nearline=self.options.fail_nearline,
            file_metadata=self.options.file_metadata,
            staging_metadata=self.options.staging_metadata,
            filesize=self.options.file_size,
            gridftp=self.options.gridftp_params,
            job_metadata=self.options.job_metadata,
            overwrite=self.options.overwrite,
            overwrite_on_retry=self.options.overwrite_on_retry,
            overwrite_hop=self.options.overwrite_hop,
            copy_pin_lifetime=self.options.pin_lifetime,
            reuse=self.options.reuse,
            retry=self.options.retry,
            multihop=self.options.multihop,
            credential=self.options.cloud_cred,
            nostreams=self.options.nostreams,
            ipv4=self.options.ipv4,
            ipv6=self.options.ipv6,
            s3alternate=self.options.s3alternate,
            target_qos=self.options.target_qos,
            buffer_size=self.options.buffer_size,
            strict_copy=self.options.strict_copy,
        )

    def _do_submit(self, context):
        if not self.options.access_token:
            delegator = Delegator(context)
            delegator.delegate(
                timedelta(minutes=self.options.proxy_lifetime),
                delegate_when_lifetime_lt=timedelta(
                    minutes=self.options.delegate_when_lifetime_lt
                ),
            )
            self.logger.debug(
                "Delegation termination time: %s"
                % delegator.get_info()["termination_time"]
            )

        submitter = Submitter(context)

        supports_overwrite_hop = True

        try:
            core = context.endpoint_info.get("core")
            if core is not None:
                major = core["major"]
                minor = core["minor"]
                supports_overwrite_hop = int(major) > 3 or (
                    int(major) == 3 and int(minor) >= 12
                )
        except Exception:
            pass  # Print compatibility warning only when fully confident

        if self.params["overwrite_hop"] and not supports_overwrite_hop:
            self.logger.warning(
                "overwrite-hop is only available for FTS Server >= 3.12.0"
            )

        job_id = submitter.submit(transfers=self.transfers, params=self.params)

        if self.options.json:
            self.logger.info(json.dumps(job_id))
        else:
            self.logger.info("Job successfully submitted.")
            self.logger.info("Job id: %s" % job_id)
        if job_id and self.options.blocking:
            inquirer = Inquirer(context)
            job = inquirer.get_job_status(job_id)
            while job["job_state"] in [
                "SUBMITTED",
                "READY",
                "STAGING",
                "ACTIVE",
                "ARCHIVING",
                "QOS_TRANSITION",
                "QOS_REQUEST_SUBMITTED",
            ]:
                self.logger.info("Job in state %s" % job["job_state"])
                time.sleep(self.options.poll_interval)
                job = inquirer.get_job_status(job_id)

            self.logger.info("Job finished with state %s" % job["job_state"])
            if job["reason"]:
                self.logger.info("Reason: %s" % job["reason"])

        return job_id

    def _do_dry_run(self, context):
        submitter = Submitter(context)
        print(submitter.build_submission(transfers=self.transfers, params=self.params))
        return None

    def run(self):
        context = self._create_context()
        if not self.options.dry_run:
            return self._do_submit(context)
        else:
            return self._do_dry_run(context)
