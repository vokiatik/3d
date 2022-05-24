import * as THREE from 'https://unpkg.com/three@0.125.0/build/three.module.js';
import { GLTFLoader } from 'https://unpkg.com/three@0.125.0/examples/jsm/loaders/GLTFLoader.js';
import { OBJLoader } from 'https://unpkg.com/three@0.125.0/examples/jsm/loaders/OBJLoader.js';
import { OrbitControls } from 'https://unpkg.com/three@0.125.0/examples/jsm/controls/OrbitControls.js';
import { MTLLoader } from 'https://unpkg.com/three@0.125.0/examples/jsm/loaders/MTLLoader.js';

// initialize constants
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({canvas: document.querySelector('#bg'),});
// const lights
const pointLight = new THREE.PointLight(0xffffff);
const ambientLight = new THREE.AmbientLight(0xffffff);
const lightHelper = new THREE.PointLightHelper(pointLight)
// const grid
const gridHelper = new THREE.GridHelper(200, 50);
//const controls
const controls = new OrbitControls(camera, renderer.domElement);
//const background
const spaceTexture = new THREE.TextureLoader().load('static/images/portrait.jpg');

// const for obj file
const loader = new OBJLoader();
const ship_material = new THREE.MeshBasicMaterial( { color: 0x444444 } );
// initialize obj model

var OBJFile = 'static/objects/house.obj';
var MTLFile = 'static/mtl/house.mtl';
var JPGFile = 'static/textures/house.png';

new MTLLoader()
.load(MTLFile, function (materials) {
    materials.preload();
    new OBJLoader()
        .setMaterials(materials)
        .load(OBJFile, function (object) {
            object.position.y = 5;
            var texture = new THREE.TextureLoader().load(JPGFile);

            object.traverse(function (child) {   // aka setTexture
                if (child instanceof THREE.Mesh) {
                    child.material.map = texture;
                }
            });
            scene.add(object);
        });
});

//configuration
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
camera.position.setZ(50);
camera.position.setX(50);
camera.position.setY(50);

renderer.render(scene, camera);

pointLight.position.set(30, 30, 30);

// Helpers
scene.background = spaceTexture;
scene.add(pointLight, ambientLight);
scene.add(lightHelper, gridHelper)

// Animation Loop
function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}

animate();