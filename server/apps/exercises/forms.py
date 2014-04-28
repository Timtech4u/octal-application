from django import forms
from models import Problems, Responses

from apps.maps.models import Graphs, Concepts

def ProblemsFormSetFactory(g=None, post=None):
    def _form_factory(g):
        """
        A closure to restrict the dependencies to those in the supplied graph
        """
        class ProblemsForm(forms.ModelForm):
            answers = forms.CharField(label=("Answers"),
                    help_text=("List all answers separated by a comma. List the correct answer first."),
                    widget=forms.Textarea(attrs={'cols':80, 'rows':2}))

            def clean_answers(self):
                """
                Validate the list of answers
                """
                # remove white space
                ans_str = "".join(self.cleaned_data['answers'].split())

                # remove leading or trailing commas, split into list
                ans = re.sub('^,|,$', '', ans_str).split(',')

                # any duplicates?
                def _list_duplicates(seq):
                    seen = set()
                    seen_add = seen.add
                    # adds all elements it doesn't know yet to seen and all other to seen_twice
                    seen_twice = set( x for x in seq if x in seen or seen_add(x) )
                    # turn the set into a list (as requested)
                    return list( seen_twice )
                dupes = _list_duplicates(ans)
                if dupes: 
                    raise forms.ValidationError("Please remove the duplicate answers: %s" % ', '.join(dupes))

                if len(ans) < 1:
                    raise forms.ValidationError("You must enter at least one answer.")

                return ans

            def __init__(self, *args, **kwargs):
                super(ProblemsForm, self).__init__(*args, **kwargs)
                self.fields['concepts'].queryset = Concepts.objects.filter(graph=g)
                self.fields['concepts'].help_text = ""

            class Meta:
                model = Problems
                labels = { 'qtype': ("Type"), }
                widgets = { 'qid': forms.HiddenInput(), }

        return ProblemsForm

    ProblemsFormSet = forms.models.inlineformset_factory(Graphs, Problems)
    ProblemsForm = ProblemsFormSet(post, instance=g)
    ProblemsForm.form = _form_factory(g)
    return ProblemsForm


