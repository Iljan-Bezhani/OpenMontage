import React from "react";
import {Composition, registerRoot} from "remotion";
import {KidsGarden, KidsGardenProps} from "./KidsGarden";

const KidsRoot: React.FC = () => (
  <Composition
    id="KidsGarden"
    component={KidsGarden}
    width={1280}
    height={720}
    fps={24}
    durationInFrames={24 * 65}
    defaultProps={{dialogue: [], duration: 65} satisfies KidsGardenProps}
    calculateMetadata={({props}) => ({
      durationInFrames: Math.max(24, Math.ceil((props.duration || 65) * 24)),
    })}
  />
);

registerRoot(KidsRoot);
