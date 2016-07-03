from django import forms

from league.models import Game
        
class GameAdminForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = '__all__'
        #widgets = {
        #    'player1': forms.Select
        #}

    class Media:
        css = {'all': ('league/css/game.css',) }
        
    result2 = forms.CharField(widget=forms.TextInput(attrs={'class': 'vIntegerField'}), label=' ')

    def __init__(self, *args, **kwargs):
        super(GameAdminForm, self).__init__(*args, **kwargs)
        for fn in ('player1', 'player2'):
            w = self.fields[fn].widget     
            self.fields[fn].widget = w.widget
        self.fields['league'].widget.widget.attrs['disabled'] = 'disabled'
        self.fields['league'].widget.can_add_related = False
