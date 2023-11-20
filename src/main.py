from datetime import datetime, timezone
import os
from typing import Any, Optional
from pypresence import Presence
import pluralkit, time, toml


config: dict[str, dict[str, Any]] = toml.load("config.toml")

# This is for the environment variable fallback
try:
	# Use token from config
	pluralkit_token: Optional[str] = config["General"]["PluralKitToken"]

	# Fallback to token from environment
	if pluralkit_token == "":
		pluralkit_token = os.environ["PLURALKIT_TOKEN"]

# Don't use a token if the config value is commented/missing
except KeyError:
	pluralkit_token: Optional[str] = None

system_id = config["General"]["PluralKitID"]

pk = pluralkit.Client(pluralkit_token, async_mode=False)


presence_client_id = config['Advanced']["ClientID"]
RPC = Presence(presence_client_id)

RPC.connect()

while True:
	switch = pk.get_switches(system_id, limit=1)[0]
	switch_first_member = switch.members[0]
	switch_member_count = len(switch.members)

	switch_dt = switch.timestamp.datetime
	# This exists because PluralKit.py doesn't manually attach UTC to its timestamps, and datetime tries to use the local timezone because of it
	switch_dt_tz = datetime(
		switch_dt.year,
		switch_dt.month,
		switch_dt.day,
		switch_dt.hour,
		switch_dt.minute,
		switch_dt.second,
		switch_dt.microsecond,
		timezone.utc)
	switch_timestamp = int(switch_dt_tz.timestamp())

	if type(switch_first_member) == pluralkit.MemberId:
		switch_first_member = pk.get_member(switch_first_member)

	RPC.update(
		state=switch_first_member.name + # type: ignore
			(f" and {switch_member_count - 1} others are fronting" if switch_member_count > 1
			else " is fronting"),
		start=switch_timestamp
	)

	time.sleep(15)