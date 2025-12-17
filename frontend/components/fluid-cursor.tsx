'use client';

import { useEffect } from 'react';
import fluidCursor from '@/hooks/use-fluid-cursor';

const FluidCursor = () => {
    useEffect(() => {
        const cleanup = fluidCursor();
        return () => {
            if (cleanup) cleanup();
        };
    }, []);

    return (
        <div className="fixed top-0 left-0 z-[-1] pointer-events-none">
            <canvas id="fluid" className="w-screen h-screen pointer-events-auto" />
        </div>
    );
};

export default FluidCursor;
