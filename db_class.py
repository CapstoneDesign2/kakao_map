import sqlalchemy as db
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

STORE_TABLE_NAME = 'store'
COMMENT_TABLE_NAME = 'comment'

Base = declarative_base()

class StoreClass(Base):
    __tablename__ = STORE_TABLE_NAME  # 데이터베이스에서 사용할 테이블 이름입니다.

    id = db.Column(db.Integer, primary_key=True)
    place_name = db.Column(db.String(50))
    phone = db.Column(db.String(30))
    x = db.Column(db.Float)
    y = db.Column(db.Float)
    #addresses = relationship("Address", back_populates="user") // 다른 테이블과 foreign key 관계일 때 사용하는거 같음
    def __init__(self, id, place_name, phone, x, y):
        self.id = id
        self.place_name = place_name
        self.phone = phone
        self.x = x
        self.y = y
    
    def __repr__(self):
       return f"User(id={self.id!r}, name={self.place_name!r}, phone={self.phone!r}, x={self.x}, y={self.y})"

class CommentCalss(Base):
    __tablename__ = COMMENT_TABLE_NAME  # 데이터베이스에서 사용할 테이블 이름입니다.

    id = db.Column(db.Integer, primary_key=True)
    contents = db.Column(db.String(100))
    point = db.Column(db.Integer)
    photoCnt = db.Column(db.Integer)
    likeCnt = db.Column(db.Integer)
    kakaoMapUserId = db.Column(db.String(100))
    # photoList
    # strengths
    userCommentCount = db.Column(db.Integer)
    userCommentAverageScore = db.Column(db.Float) # 정확도 크게 상관 없음
    date = db.Column(db.String(10)) # 이거 맞나? . . 으로 분리되어서 date 를 나타냄
    store_id = db.ForeignKey(f'{STORE_TABLE_NAME}.id')
    
    #addresses = relationship("Address", back_populates="user") // 아직은 코드상에서 댓글로 사용자 찾는 경우는 없는 것 같으니 사용하지 않는다.
    def __init__(self, id, contents, point, photoCnt, likeCnt, kakaoMapUserId, photoList="", strengths="", userCommentCount=0, userCommentAverageScore=0.0, date="", store_id=0):
        self.id = id
        self.contents = contents
        self.point = point
        self.photoCnt = photoCnt
        self.likeCnt = likeCnt
        self.kakaoMapUserId = kakaoMapUserId
        #self.photoList = photoList # 이거 저장 방식 json
        #self.strengths = strengths
        self.userCommentCount = userCommentCount
        self.userCommentAverageScore = userCommentAverageScore
        self.date = date
        self.store_id = store_id
        
    def __repr__(self):
       return f"User(id={self.id!r}, name={self.place_name!r}, phone={self.phone!r}, x={self.x}, y={self.y})"
