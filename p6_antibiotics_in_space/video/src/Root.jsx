import React from 'react';
import {Composition} from 'remotion';
import {Film} from './Film';
export const Root = () => (
  <Composition id="Antibiotics" component={Film} durationInFrames={1230} fps={30} width={1920} height={1080} />
);
