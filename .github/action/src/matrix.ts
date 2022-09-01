/**
 * Scenario
 * matrix is empty
 * use both history and fallback to fill the entry
 * create a diff for history file
 * save all
 */
import {readFileSync} from 'node:fs';
import path from 'node:path';
import {load} from 'js-yaml';
import {execSync} from 'child_process';

import type {
  IFallback,
  IHistory,
  IMatrix,
  IMatrixEntry,
  Options,
} from './types';
import {ReleaseHistory} from './release_history';

class Matrix {
  private _matrix!: IMatrix;
  private _previous!: IMatrixEntry;
  private _final!: IMatrixEntry;

  private _fallback!: IFallback;
  private _history!: ReleaseHistory;

  constructor(matrix: string, fallback: string, history: string) {
    this._matrix = load(
      readFileSync(path.join(__dirname, '.github', matrix)).toString()
    ) as IMatrix;
    this._fallback = load(
      readFileSync(path.join(__dirname, '.github', fallback)).toString()
    ) as IFallback;

    this._history = new ReleaseHistory(history);

    const previous = this._matrix.at(-2);
    if (previous) {
      this._previous = previous;
    }
    const final = this._matrix.at(-2);
    if (final) {
      this._final = final;
    }
  }

  private getOption(opt: Options): string {
    if (this._final[opt]) {
      return this._final[opt];
    }

    const fallback = this._fallback[opt];
    if (!fallback) {
      throw new Error(`option ${opt} not found; fallback missed`);
    }

    if (fallback.$shell) {
      return execSync(fallback.$shell).toString();
    }

    if (fallback.$last) {
      // TODO check history
    }

    if (fallback.$previous) {
      // check previous entry
      if (!this._previous[opt]) {
        throw new Error(
          `option ${opt} not found; fallback $previous detected no value`
        );
      }
      return this._previous[opt];
    }

    throw new Error('unknown error');
  }
}
