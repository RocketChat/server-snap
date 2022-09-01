export interface IMatrixEntry {
  version: string;
  epoch: string;
  migrations: string[];
  nodejs: {
    version: string;
    link: string;
  };
  mongodb: {
    server: {
      version: string;
      link: string;
    };
  };
}

export type IMatrix = IMatrixEntry[];

export interface IHistoryEntry {
  version: {incremented: string; decremented: string; repeated: string};
  epoch: {incremented: string; decremented: string; repeated: string};
  migrations: {
    pre: {enabled: boolean; disabled: boolean};
    post: {enabled: boolean; disabled: boolean};
  };
  nodejs: {
    changed: {
      version: {incremented: string; decremented: string; repeated: string};
      link: {repeated: string; changed: string};
    };
    repeated: {
      version: {incremented: string; decremented: string; repeated: string};
      link: {repeated: string; changed: string};
    };
  };
  mongodb: {
    changed: {
      version: {incremented: string; decremented: string; repeated: string};
      link: {repeated: string; changed: string};
    };
    repeated: {
      version: {incremented: string; decremented: string; repeated: string};
      link: {repeated: string; changed: string};
    };
  };
}

export type IHistory = IHistoryEntry[];

interface IFallBackOptions {
  $shell: string;
  // whenever last it was non-empty
  $last: string;
}
export interface IFallback {
  version: IFallBackOptions;
  epoch: IFallBackOptions;
}

export type Options = keyof IFallback;

export enum DiffType {
  INCREASES = 1,
  DECREASED = -1,
  EQUAL = 0,
  CHANGED = 2,
}
