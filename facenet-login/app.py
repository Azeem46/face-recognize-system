from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from facenet_pytorch import MTCNN, InceptionResnetV1
import torch, numpy as np, os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
mtcnn = MTCNN(image_size=160, margin=0)
resnet = InceptionResnetV1(pretrained='vggface2').eval()

EMB_DIR = 'embeddings'
os.makedirs(EMB_DIR, exist_ok=True)

def save_embedding(name, emb):
    np.save(f"{EMB_DIR}/{name}.npy", emb)

def load_embeddings():
    return { f[:-4]: np.load(f"{EMB_DIR}/{f}") for f in os.listdir(EMB_DIR) if f.endswith('.npy') }

def get_embedding(img):
    print('Image type:', type(img))
    print('Image size:', getattr(img, 'size', None))
    # detect face, align to 160x160, return 512-d
    face = mtcnn(img)
    print('Face tensor:', face)
    if face is None: return None
    emb = resnet(face.unsqueeze(0)).detach().numpy()[0]
    return emb / np.linalg.norm(emb)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method=='POST':
        name = request.form.get('name')
        img_data = request.files['image'].read()
        print('Received image bytes:', len(img_data))
        import io, PIL.Image
        img = PIL.Image.open(io.BytesIO(img_data))
        print('Opened image:', img)
        img.save(f'{EMB_DIR}/debug_received.jpg')
        emb = get_embedding(img)
        if emb is None: return jsonify({'status':'no_face'})
        save_embedding(name, emb); return jsonify({'status':'ok'})
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        img_data = request.files['image'].read()
        import io, PIL.Image
        img = PIL.Image.open(io.BytesIO(img_data))
        emb = get_embedding(img)
        if emb is None: return jsonify({'status':'no_face'})
        users = load_embeddings()
        if not users: return jsonify({'status':'none_registered'})
        sims = {u: np.dot(emb, e) for u,e in users.items()}
        name, score = max(sims.items(), key=lambda p:p[1])
        if score > 0.8:
            session['user']=name; return jsonify({'status':'ok','user':name})
        return jsonify({'status':'not_recognized'})
    if 'user' in session: return f"Hello, {session['user']}!"
    return render_template('login.html')

@app.route('/welcome')
def welcome():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('welcome.html')

@app.route('/logout')
def logout():
    session.pop('user',None); return redirect(url_for('login'))

if __name__=='__main__':
    app.run(debug=True)
