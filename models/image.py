from db import db


class ItemImageModel(db.Model):
    __tablename__ = "images"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    image = db.Column(db.String(80))

    item_id = db.Column(db.Integer, db.ForeignKey("items.id"))
    item = db.relationship("ItemModel", back_populates="images")

    def __init__(self, title, image, item_id):
        self.title = title
        self.image = image
        self.item_id = item_id

    def json(self):
        return {
            "id": self.id,
            "title": self.name,
            "image": self.image,
        }

    @classmethod
    def find_by_title(cls, title):
        return cls.query.filter_by(title=title).first()

    @classmethod
    def find_all(cls):
        return cls.query.all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
