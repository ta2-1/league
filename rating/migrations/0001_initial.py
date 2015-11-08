# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Rule'
        db.create_table('rating_rule', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('text', self.gf('django.db.models.fields.TextField')(default='')),
        ))
        db.send_create_signal('rating', ['Rule'])

        # Adding model 'Competitor'
        db.create_table('rating_competitor', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('firstName', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('lastName', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('birthDate', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rating.Category'])),
        ))
        db.send_create_signal('rating', ['Competitor'])

        # Adding model 'Category'
        db.create_table('rating_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=25)),
        ))
        db.send_create_signal('rating', ['Category'])

        # Adding model 'Location'
        db.create_table('rating_location', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('latitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('longitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal('rating', ['Location'])

        # Adding model 'Tournament'
        db.create_table('rating_tournament', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('end_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('squashclub_url', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('is_past', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('rating', ['Tournament'])

        # Adding model 'ResultSet'
        db.create_table('rating_resultset', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tournament', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rating.Tournament'])),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rating.Category'])),
        ))
        db.send_create_signal('rating', ['ResultSet'])

        # Adding M2M table for field locations on 'ResultSet'
        db.create_table('rating_resultset_locations', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('resultset', models.ForeignKey(orm['rating.resultset'], null=False)),
            ('location', models.ForeignKey(orm['rating.location'], null=False))
        ))
        db.create_unique('rating_resultset_locations', ['resultset_id', 'location_id'])

        # Adding model 'Results'
        db.create_table('rating_results', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('competitor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rating.Competitor'])),
            ('resultset', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rating.ResultSet'])),
            ('place', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal('rating', ['Results'])


    def backwards(self, orm):
        
        # Deleting model 'Rule'
        db.delete_table('rating_rule')

        # Deleting model 'Competitor'
        db.delete_table('rating_competitor')

        # Deleting model 'Category'
        db.delete_table('rating_category')

        # Deleting model 'Location'
        db.delete_table('rating_location')

        # Deleting model 'Tournament'
        db.delete_table('rating_tournament')

        # Deleting model 'ResultSet'
        db.delete_table('rating_resultset')

        # Removing M2M table for field locations on 'ResultSet'
        db.delete_table('rating_resultset_locations')

        # Deleting model 'Results'
        db.delete_table('rating_results')


    models = {
        'rating.category': {
            'Meta': {'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '25'})
        },
        'rating.competitor': {
            'Meta': {'object_name': 'Competitor'},
            'birthDate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rating.Category']"}),
            'firstName': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastName': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        'rating.location': {
            'Meta': {'object_name': 'Location'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        'rating.results': {
            'Meta': {'object_name': 'Results'},
            'competitor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rating.Competitor']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'place': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'resultset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rating.ResultSet']"})
        },
        'rating.resultset': {
            'Meta': {'object_name': 'ResultSet'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rating.Category']"}),
            'competitors': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'resultsets'", 'symmetrical': 'False', 'through': "orm['rating.Results']", 'to': "orm['rating.Competitor']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locations': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'resultsets'", 'symmetrical': 'False', 'to': "orm['rating.Location']"}),
            'tournament': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rating.Tournament']"})
        },
        'rating.rule': {
            'Meta': {'object_name': 'Rule'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'default': "''"})
        },
        'rating.tournament': {
            'Meta': {'object_name': 'Tournament'},
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_past': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'squashclub_url': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        }
    }

    complete_apps = ['rating']
