import {load} from 'js-yaml';
import {readFileSync} from 'fs';
import path from 'node:path';

import type {IHistory, IHistoryEntry} from './types';

export class ReleaseHistory {
  private _history!: IHistory;
  private _last!: IHistoryEntry;

  constructor(history: string) {
    this._history = load(
      readFileSync(path.join(__dirname, '.github', history)).toString()
    ) as IHistory;
    const last = this._history.at(-1);
    if (last) {
      this._last = last;
    }
  }

  public getOption(opt: any): string {}

  public save(): void {}
}
