This document guides one through the process of upgrading the snap with a new version.

It takes care of
1. Rocket.Chat version
2. MongoDB version
3. Node.js version

**0. Fetch the old mongodb version, install required tools**

It should be available in `rocket_craft/parts-{rocketchat_version}.yaml`, look at `mongodb-version` property under `mongodb` part.

Also install `direnv` for easier environment management <https://direnv.net>.

Once you `cd` into this repository, run `direnv allow .` to load the environment.

You can run `source ._rocketcraft_completion.bash` to load the completion for `rocketcraft` command if using `bash` for shell, or use `source ._rocketcraft_completion.zsh` if using `zsh`.

**1. Prepare the artifacts for new build**

Run the following command
```sh
rocketcraft rocketchat prepare \
--craft-file snap/snapcraft.yaml \
--version <new_rocketchat_version> \
--current-mongodb-version <old_mongodb_version>
```

Pass `--skip-run` to skip the run step, this is useful if you are not using an ubuntu based system;

This will
1. Find the next upgradable MongoDB version
2. Update epoch depending on \#1
3. Update/add the part file for mongodb and nodejs

**2. Build the snap**

Run the following command
```sh
snapcraft pack
```

This will pack the snap and save it to `rocketchat-server_<new_rocketchat_version>_amd64.snap`.
