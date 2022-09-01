import {IMigration} from './types';
import path from 'node:path';
import fs from 'node:fs/promises';
import {constants} from 'fs';

type MigrationProps = {
  pre: string[];
  post: string[];
};

export class Migrations implements IMigration {
  public enabled: string[] = [];
  public disabled: string[] = [];

  public diff: boolean = false; // if anything changes, set to true; this marks one part of any need for commiting tp repo

  constructor(entry: MigrationProps) {
    (['pre', 'post'] as const).forEach((triggerMoment: 'pre' | 'post') => {
      for (const migration in entry[triggerMoment]) {
        if (migration.startsWith('-')) {
          this.disabled.push(
            path.join(
              __dirname,
              'migrations',
              `${triggerMoment}_refresh`,
              migration.substring(1)
            )
          );
          continue;
        }

        this.enabled.push(
          path.join(
            __dirname,
            'migrations',
            `${triggerMoment}_refresh`,
            migration
          )
        );
      }
    });
  }

  private async enableMigrations() {
    return Promise.all(
      this.enabled.map(
        (enabled) =>
          new Promise((resolve) =>
            fs.access(enabled, constants.X_OK).catch((_) => {
              this.diff = true; // having to change file
              resolve(
                fs.chmod(
                  enabled,
                  constants.S_IXUSR | constants.S_IXGRP | constants.S_IXOTH
                )
              );
            })
          )
      )
    );
  }

  private async disableMigrations() {
    return Promise.all(
      this.disabled.map(
        (enabled) =>
          new Promise((resolve) =>
            fs.access(enabled, constants.X_OK).then(() => {
              this.diff = true; // having to change file
              resolve(
                fs.chmod(
                  enabled,
                  constants.S_IRUSR | constants.S_IRGRP | constants.S_IROTH
                )
              );
            })
          )
      )
    );
  }

  private async resolveMigrations(): Promise<void> {
    await Promise.all([this.enableMigrations(), this.disableMigrations()]);
  }
}
