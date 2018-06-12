from django import template

register = template.Library()

@register.filter(name='youtube_view_url')
@register.assignment_tag
def youtube_view_url(youtube_movie):
    idx = youtube_movie.rfind('/')
    movie_id = youtube_movie[idx + 1:]
    if not movie_id:
        idx = youtube_movie[:-1].rfind('/')
        movie_id = youtube_movie[idx + 1:-1]
    return 'https:///www.youtube-nocookie.com/embed/' + movie_id + '?rel=0&controls=0'
    
