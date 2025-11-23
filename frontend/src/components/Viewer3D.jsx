import React, { Suspense, useEffect } from 'react';
import { Canvas, useLoader } from '@react-three/fiber';
import { OrbitControls, Stage } from '@react-three/drei';
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader';
import * as THREE from 'three';

function Model({ url }) {
    const geometry = useLoader(STLLoader, url);

    useEffect(() => {
        geometry.center();
        geometry.computeVertexNormals();
    }, [geometry]);

    return (
        <mesh geometry={geometry} castShadow receiveShadow>
            <meshStandardMaterial
                color="#7cc7ff"
                metalness={0.1}
                roughness={0.6}
                side={THREE.DoubleSide}
            />
        </mesh>
    );
}

export default function Viewer3D({ modelUrl }) {
    return (
        <div className="w-full h-full bg-gray-900">
            <Canvas shadows camera={{ position: [0, 0, 150], fov: 50 }}>
                <ambientLight intensity={0.3} />
                <pointLight position={[50, 50, 50]} intensity={0.8} />
                <Suspense fallback={null}>
                    <Stage environment="city" intensity={0.5} adjustCamera shadows={false}>
                        {modelUrl ? (
                            <Model url={modelUrl} />
                        ) : (
                            <mesh>
                                <boxGeometry args={[10, 10, 10]} />
                                <meshStandardMaterial color="#444" wireframe />
                            </mesh>
                        )}
                    </Stage>
                </Suspense>
                <OrbitControls makeDefault />
            </Canvas>
        </div>
    );
}
