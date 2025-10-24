from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from blog.models import Category, Blog
from django.utils import timezone
from django.utils.text import slugify

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate the database with sample blog data'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')

        # Create sample categories
        categories_data = [
            {
                'title': 'Technology',
                'meta_description': 'Latest technology trends and innovations',
                'meta_keywords': 'technology, innovation, tech news, programming'
            },
            {
                'title': 'Lifestyle',
                'meta_description': 'Lifestyle tips and personal development',
                'meta_keywords': 'lifestyle, personal development, tips, wellness'
            },
            {
                'title': 'Travel',
                'meta_description': 'Travel guides and destination reviews',
                'meta_keywords': 'travel, destinations, guides, tourism'
            },
            {
                'title': 'Food & Cooking',
                'meta_description': 'Delicious recipes and cooking tips',
                'meta_keywords': 'food, cooking, recipes, culinary'
            },
            {
                'title': 'Business',
                'meta_description': 'Business insights and entrepreneurship',
                'meta_keywords': 'business, entrepreneurship, finance, marketing'
            }
        ]

        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                title=cat_data['title'],
                defaults={
                    'slug': slugify(cat_data['title']),
                    'meta_description': cat_data['meta_description'],
                    'meta_keywords': cat_data['meta_keywords'],
                    'is_active': True
                }
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Created category: {category.title}')

        # Create a sample user if none exists
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@blogplatform.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            user.set_password('admin123')
            user.save()
            self.stdout.write('Created admin user: admin/admin123')

        # Create sample blog posts
        blog_posts_data = [
            {
                'title': 'The Future of Web Development',
                'excerpt': 'Exploring the latest trends and technologies shaping the future of web development.',
                'description': '''# The Future of Web Development

Web development is evolving at an unprecedented pace. From the rise of **JavaScript frameworks** to the adoption of **WebAssembly**, developers are constantly adapting to new technologies.

## Key Trends

### 1. Progressive Web Apps (PWAs)
PWAs are bridging the gap between web and mobile applications, offering:
- Offline functionality
- Push notifications
- App-like experience

### 2. Serverless Architecture
Serverless computing is revolutionizing how we build applications:
- Reduced infrastructure management
- Automatic scaling
- Pay-per-use pricing

### 3. AI Integration
Artificial Intelligence is becoming integral to web development:
- Automated testing
- Code generation
- User experience optimization

## Conclusion

The future of web development is exciting and full of possibilities. Staying updated with these trends is crucial for any developer looking to build modern, efficient applications.''',
                'category': categories[0],  # Technology
                'featured': True,
                'meta_description': 'Explore the latest trends and technologies shaping the future of web development',
                'meta_keywords': 'web development, javascript, PWAs, serverless, AI'
            },
            {
                'title': '10 Tips for Better Work-Life Balance',
                'excerpt': 'Practical strategies to achieve a healthier balance between your professional and personal life.',
                'description': '''# 10 Tips for Better Work-Life Balance

Achieving work-life balance is essential for maintaining mental health and overall well-being. Here are ten practical strategies:

## 1. Set Clear Boundaries
- Define work hours and stick to them
- Create a dedicated workspace
- Learn to say "no" when necessary

## 2. Prioritize Your Tasks
- Use the Eisenhower Matrix
- Focus on high-impact activities
- Delegate when possible

## 3. Take Regular Breaks
- Follow the Pomodoro Technique
- Take lunch breaks away from your desk
- Use vacation days

## 4. Practice Mindfulness
- Start your day with meditation
- Practice deep breathing exercises
- Stay present in the moment

## 5. Maintain Healthy Relationships
- Schedule quality time with family
- Nurture friendships
- Communicate openly

## Conclusion

Remember, work-life balance is a journey, not a destination. Start implementing these tips gradually and adjust as needed.''',
                'category': categories[1],  # Lifestyle
                'featured': False,
                'meta_description': 'Practical strategies to achieve a healthier balance between work and personal life',
                'meta_keywords': 'work-life balance, productivity, mindfulness, wellness'
            },
            {
                'title': 'Hidden Gems of Southeast Asia',
                'excerpt': 'Discover the lesser-known but equally stunning destinations in Southeast Asia.',
                'description': '''# Hidden Gems of Southeast Asia

Southeast Asia is home to some of the world's most beautiful destinations. While popular spots like Bali and Bangkok are well-known, there are many hidden gems waiting to be discovered.

## Must-Visit Hidden Destinations

### 1. Koh Rong Sanloem, Cambodia
- Pristine beaches
- Crystal clear waters
- Peaceful atmosphere

### 2. El Nido, Philippines
- Stunning limestone cliffs
- Secret lagoons
- World-class diving

### 3. Luang Prabang, Laos
- UNESCO World Heritage Site
- Traditional architecture
- Rich cultural heritage

### 4. Hpa-An, Myanmar
- Cave temples
- Limestone mountains
- Authentic local experience

## Travel Tips

- Respect local customs and traditions
- Pack light and appropriately
- Learn basic local phrases
- Support local businesses

## Conclusion

These hidden gems offer authentic experiences away from the crowds. Plan your visit during the dry season for the best weather.''',
                'category': categories[2],  # Travel
                'featured': True,
                'meta_description': 'Discover the lesser-known but equally stunning destinations in Southeast Asia',
                'meta_keywords': 'Southeast Asia, travel, hidden gems, destinations, tourism'
            },
            {
                'title': 'Mastering the Art of Sourdough Bread',
                'excerpt': 'Learn the secrets to creating perfect sourdough bread at home with this comprehensive guide.',
                'description': '''# Mastering the Art of Sourdough Bread

Sourdough bread making is both an art and a science. With patience and practice, you can create bakery-quality loaves at home.

## Getting Started

### Creating Your Starter
1. Mix equal parts flour and water
2. Feed daily for 7-10 days
3. Look for bubbles and sour smell
4. Store in refrigerator when active

### Essential Equipment
- Digital kitchen scale
- Dutch oven or bread pan
- Bench scraper
- Proofing basket (banneton)

## The Process

### Day 1: Autolyse
- Mix flour and water
- Let rest for 30-60 minutes
- This develops gluten naturally

### Day 1: Mixing
- Add starter and salt
- Mix until smooth
- Perform stretch and folds

### Day 1: Bulk Fermentation
- Let rise for 4-6 hours
- Perform folds every 30 minutes
- Watch for 50% volume increase

### Day 2: Shaping and Baking
- Shape into boule or batard
- Proof for 2-4 hours
- Bake at 450°F for 30 minutes

## Troubleshooting

**Dense bread**: Under-proofed or weak starter
**Too sour**: Over-fermented or old starter
**Flat loaf**: Over-proofed or weak gluten

## Conclusion

Perfect sourdough takes time to master. Don't be discouraged by early failures - each loaf teaches you something new!''',
                'category': categories[3],  # Food & Cooking
                'featured': False,
                'meta_description': 'Learn the secrets to creating perfect sourdough bread at home',
                'meta_keywords': 'sourdough, bread making, baking, fermentation, cooking'
            },
            {
                'title': 'Building a Successful Startup: Lessons Learned',
                'excerpt': 'Key insights from building a startup from the ground up, including common pitfalls and success strategies.',
                'description': '''# Building a Successful Startup: Lessons Learned

Starting a business is one of the most challenging yet rewarding endeavors. Here are the key lessons learned from building a successful startup.

## The Foundation

### 1. Solve a Real Problem
- Identify genuine pain points
- Validate with potential customers
- Focus on user needs, not technology

### 2. Build a Strong Team
- Hire for cultural fit
- Look for complementary skills
- Foster open communication

### 3. Secure Funding Strategically
- Bootstrap when possible
- Choose investors carefully
- Maintain control of your vision

## Growth Strategies

### Customer Acquisition
- Focus on one channel initially
- Measure and optimize constantly
- Build referral programs

### Product Development
- Ship early and often
- Gather user feedback
- Iterate based on data

### Scaling Operations
- Automate repetitive tasks
- Build scalable systems
- Hire ahead of growth

## Common Pitfalls

1. **Premature Scaling**: Growing too fast without solid foundations
2. **Feature Creep**: Adding too many features too quickly
3. **Ignoring Metrics**: Not tracking key performance indicators
4. **Poor Cash Management**: Running out of money unexpectedly

## Success Metrics

- Monthly Recurring Revenue (MRR)
- Customer Acquisition Cost (CAC)
- Customer Lifetime Value (CLV)
- Net Promoter Score (NPS)

## Conclusion

Building a startup requires resilience, adaptability, and continuous learning. Focus on solving real problems and building sustainable businesses.''',
                'category': categories[4],  # Business
                'featured': True,
                'meta_description': 'Key insights from building a startup from the ground up',
                'meta_keywords': 'startup, entrepreneurship, business, funding, growth'
            }
        ]

        for post_data in blog_posts_data:
            blog, created = Blog.objects.get_or_create(
                title=post_data['title'],
                defaults={
                    'slug': slugify(post_data['title']),
                    'category': post_data['category'],
                    'author': user,
                    'description': post_data['description'],
                    'excerpt': post_data['excerpt'],
                    'featured': post_data['featured'],
                    'meta_description': post_data['meta_description'],
                    'meta_keywords': post_data['meta_keywords'],
                    'is_active': True,
                    'reading_time': len(post_data['description'].split()) // 200 + 1
                }
            )
            if created:
                self.stdout.write(f'Created blog post: {blog.title}')

        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        )
        self.stdout.write('You can now visit the admin panel to manage your content.')
