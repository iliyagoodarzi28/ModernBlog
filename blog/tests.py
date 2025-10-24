from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from blog.models import Category, Blog

User = get_user_model()


class BlogModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            title='Test Category',
            slug='test-category',
            meta_description='Test category description'
        )

    def test_category_creation(self):
        """Test category creation with automatic slug generation"""
        category = Category.objects.create(
            title='New Category',
            meta_description='A new test category'
        )
        self.assertEqual(category.slug, slugify(category.title))
        self.assertTrue(category.is_active)
        self.assertFalse(category.is_deleted)

    def test_blog_creation(self):
        """Test blog post creation with all new fields"""
        blog = Blog.objects.create(
            title='Test Blog Post',
            category=self.category,
            author=self.user,
            description='This is a test blog post content.',
            excerpt='Test excerpt',
            meta_description='Test meta description',
            meta_keywords='test, blog, post',
            featured=True
        )
        
        self.assertEqual(blog.slug, slugify(blog.title))
        self.assertEqual(blog.author, self.user)
        self.assertEqual(blog.category, self.category)
        self.assertTrue(blog.featured)
        self.assertEqual(blog.views, 0)
        self.assertTrue(blog.is_active)

    def test_blog_excerpt_method(self):
        """Test the get_excerpt method"""
        blog = Blog.objects.create(
            title='Test Blog',
            category=self.category,
            author=self.user,
            description='This is a test blog post with some content.',
            excerpt='Custom excerpt'
        )
        
        # Should return custom excerpt when available
        self.assertEqual(blog.get_excerpt(), 'Custom excerpt')
        
        # Should return truncated description when no excerpt
        blog.excerpt = ''
        blog.save()
        excerpt = blog.get_excerpt()
        self.assertIn('This is a test blog post', excerpt)
        self.assertTrue(len(excerpt) <= 203)  # 200 + "..."

    def test_blog_view_increment(self):
        """Test view increment functionality"""
        blog = Blog.objects.create(
            title='Test Blog',
            category=self.category,
            author=self.user,
            description='Test content'
        )
        
        initial_views = blog.views
        blog.increment_views()
        blog.refresh_from_db()
        
        self.assertEqual(blog.views, initial_views + 1)

    def test_blog_absolute_url(self):
        """Test blog absolute URL generation"""
        blog = Blog.objects.create(
            title='Test Blog',
            category=self.category,
            author=self.user,
            description='Test content'
        )
        
        expected_url = f'/blog/detail/{blog.slug}/'
        self.assertEqual(blog.get_absolute_url(), expected_url)