from app import db, logger

class Video(db.Model):
	__tablename__ = 'video'
	id = db.Column(db.Integer, primary_key=True)
	duration = db.Column(db.Integer, nullable=False)
	# Time stored in "mysterious nanosecond time"
	time = db.Column(db.Integer, nullable=False)
	video_path = db.Column(db.String(100), nullable=False)
	tester_id = db.Column(db.Integer, db.ForeignKey('tester.id'), nullable=False)
	tester = db.relationship("Tester", back_populates="video")


class Tester(db.Model):

	__tablename__ = 'tester'
	id = db.Column(db.Integer, primary_key=True)
	time = db.Column(db.String(40), nullable=False)
	phone_manufacturer = db.Column(db.String(40), nullable=False)
	phone_model = db.Column(db.String(20), nullable=False)
	screen_height = db.Column(db.Integer, nullable=False)
	screen_width = db.Column(db.Integer, nullable=False)
	test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)
	pictures = db.relationship('Picture', backref='tester', lazy=True)
	video = db.relationship("Video", uselist=False, back_populates="tester")

	@property
	def video_uploaded(self):
		"""
		True/False depending on whether associated video
		has a path stored in the db. 
		"""
		if self.video.image_path:
			return True
		return False


	@property
	def pictures_uploaded(self):
		"""
		True/False depending on whether each picture associated with a tester
		has an associated path. False indicates some error in uploading
		"""
		for picture in self.pictures:
			if picture.image_path is None:
				logger(picture.image_path)
				return False
		return True


class Picture(db.Model):
	__tablename__ = 'picture'
	__table_args__ = (
		# Enforces a picture's time is unique per user
		db.UniqueConstraint('tester_id', 'time'),
		)
	id = db.Column(db.Integer, primary_key=True)
	height = db.Column(db.Integer, nullable=False)
	width = db.Column(db.Integer, nullable=False)
	pic_num = db.Column(db.Integer, nullable=False)
	# Time stored in "mysterious nanosecond time"
	time = db.Column(db.Integer, nullable=False)
	# Allow image path to be null, as we won't set it
	# till after image is uploaded, and will use this to flag
	# if image is successfully uploaded
	image_path = db.Column(db.String(100))
	tester_id = db.Column(db.Integer, db.ForeignKey('tester.id'), nullable=False)


class Test(db.Model):
	__tablename__ = 'test'
	id = db.Column(db.Integer, primary_key=True)
	# Name is nullable in case where we create a test implicitly
	name = db.Column(db.String(80), unique=True)
	testers = db.relationship('Tester', backref='test', lazy=True)


if __name__ == "__main__":

    # Run this file directly to create the database tables.
    print("Creating database tables...")
    db.create_all()
    print("Done!")