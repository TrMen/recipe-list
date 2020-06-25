import unittest
from app import db, app
from app.models import User, Tag, Recipe


class UserModelCase(unittest.TestCase):
    def setUp(self) -> None:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://' # Set up an in-memory db
        db.create_all()

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self):
        u = User('susan', 'susansmail@gmail.com')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_recipe_control(self):
        u = User('testUser', 'testEmail@gmail.com')
        db.session.add(u)
        db.session.commit()     # So that ids get assigned
        r = Recipe('recipe1', u.id)
        db.session.add(r)

        self.assertEqual(u.recipes.filter(Recipe.user_id == u.id).count(), 1)
        self.assertEqual(r.author, u)


class RecipeModelCase(unittest.TestCase):
    def setUp(self) -> None:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()
        self.testUser = User('bob', 'bobsmail@gmail.com')
        self.testRecipe = Recipe("Bob's Recipe", self.testUser.id)
        db.session.add_all([self.testUser, self.testRecipe])

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()

    def test_uuid(self):
        r1 = Recipe('testRecipe1', self.testUser.id)
        r2 = Recipe('testRecipe2', self.testUser.id)
        db.session.add_all([r1, r2])
        self.assertNotEqual(r1.uuid, r2.uuid)
        self.assertEqual(Recipe.query.filter(Recipe.uuid == r1.uuid).count(), 1)

    def test_tagging(self):
        t1 = Tag('testTag1')
        db.session.add(t1)
        self.assertFalse(self.testRecipe.has_tag(t1))
        self.testRecipe.add_tag(t1)
        self.assertTrue(self.testRecipe.has_tag(t1))
        self.assertTrue(t1 in self.testRecipe.tags.filter(Tag.id == self.testRecipe.id).all())
        self.assertEqual(self.testRecipe.tags.filter(Tag.id == t1.id).count(), 1)
        self.testRecipe.remove_tag(t1)
        self.assertFalse(self.testRecipe.has_tag(t1))


if __name__ == '__main__':
    unittest.main(verbosity=2)
