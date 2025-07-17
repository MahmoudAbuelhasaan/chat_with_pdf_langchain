from app import create_app,db,socketio



app = create_app()

if __name__=="__main__":
    with app.app_context():
        from app import models
        db.create_all()
    socketio.run(app,debug=True,host='0.0.0.0',port=5000)