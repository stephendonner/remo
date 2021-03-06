import datetime

from django.contrib import messages
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache

import forms
import remo.base.utils as utils
from remo.base.decorators import permission_check
from models import Report, ReportComment


@never_cache
def view_report(request, display_name, year, month):
    """View report view."""
    month_number = utils.month2number(month)
    report = get_object_or_404(Report,
                               user__userprofile__display_name=display_name,
                               month__year=int(year),
                               month__month=month_number)

    if request.method == 'POST':
        if not request.user.is_authenticated():
            messages.error(request, 'Permission denied.')
            return redirect('main')

        report_comment = ReportComment(report=report, user=request.user)
        report_comment_form = forms.ReportCommentForm(request.POST,
                                                      instance=report_comment)
        if report_comment_form.is_valid():
            report_comment_form.save()
            messages.success(request, 'Comment saved.')

            # provide a new clean form
            report_comment_form = forms.ReportCommentForm()
    else:
        report_comment_form = forms.ReportCommentForm()

    report_url = reverse('reports_view_report',
                         kwargs={'display_name': display_name,
                                 'year': year,
                                 'month': month})

    if (request.user.groups.filter(name='Admin').exists() or
        (request.user == report.user) or
        (request.user.is_authenticated() and
         report.user in request.user.mentees.all())):
        editable = True
    else:
        editable = False

    q = Q(name='Admin') | Q(name='Council') | Q(name='Mentor')
    if (request.user.groups.filter(q).exists() or request.user == report.user):
        view_status = True
    else:
        view_status = False

    return render(request, 'view_report.html',
                  {'pageuser': report.user,
                   'user_profile': report.user.userprofile,
                   'editable': editable,
                   'view_status': view_status,
                   'report': report,
                   'month': month,
                   'year': year,
                   'comments': report.reportcomment_set.all(),
                   'report_comment_form_url': report_url,
                   'report_comment_form': report_comment_form})


@permission_check(permissions=['reports.can_delete_reports'])
def delete_report_comment(request, display_name, year, month, comment_id):
    """Delete report comment view."""
    if request.method == 'POST':
        if comment_id:
            report_comment = get_object_or_404(ReportComment, pk=comment_id)
            report_comment.delete()
            messages.success(request, 'Comment successfully deleted.')

    report_url = reverse('reports_view_report',
                         kwargs={'display_name': display_name,
                                 'year': year,
                                 'month': month})
    return redirect(report_url)


@permission_check(permissions=['reports.can_delete_reports'])
def delete_report(request, display_name, year, month):
    """Delete report view."""
    if request.method == 'POST':
        user = get_object_or_404(User, userprofile__display_name=display_name)
        year_month = datetime.datetime(year=int(year),
                                       month=utils.month2number(month), day=1)
        report = get_object_or_404(Report, user=user, month=year_month)
        report.delete()
        messages.success(request, 'Report successfully deleted.')

    if request.user == user:
        return redirect('profiles_view_my_profile')
    else:
        redirect_url = reverse(
            'profiles_view_profile',
            kwargs={'display_name': user.userprofile.display_name})
        return redirect(redirect_url)


@never_cache
@permission_check(permissions=['reports.can_edit_reports'],
                  display_name_field='display_name')
def edit_report(request, display_name, year, month):
    """Edit report view."""
    user = get_object_or_404(User, userprofile__display_name=display_name)
    year_month = datetime.datetime(year=int(year),
                                   month=utils.month2number(month), day=1)
    today = datetime.datetime.today()

    # check if it's too early to file this report
    if (((year_month.month > today.month) or
         (year_month.month == today.month and today.day < 23)) and
        year_month.year >= today.year):
        messages.error(request, 'I\'m sorry, are you from the future?')
        if request.user == user:
            return redirect('profiles_view_my_profile')
        else:
            redirect_url = reverse('profiles_view_profile',
                                   kwargs={'display_name': display_name})
            return redirect(redirect_url)


    report, created = utils.get_or_create_instance(Report, user=user,
                                                   month=year_month)

    if request.method == 'POST':
        # Make sure that users without permission do not modify
        # overdue field.
        data = request.POST.copy()
        if not request.user.has_perm('reports.can_edit_report'):
            data['overdue'] = report.overdue

        report_form = forms.ReportForm(data, instance=report)
        report_event_formset = forms.ReportEventFormset(data, instance=report)
        report_link_formset = forms.ReportLinkFormset(data, instance=report)

        if (report_form.is_valid() and report_event_formset.is_valid() and
            report_link_formset.is_valid()):
            report_form.save()
            report_event_formset.save()
            report_link_formset.save()

            if created:
                messages.success(request, 'Report successfully created.')
            else:
                messages.success(request, 'Report successfully updated.')

            return redirect(reverse('reports_view_report',
                                    kwargs={'display_name': display_name,
                                            'year': year,
                                            'month': month}))
    else:
        report_form = forms.ReportForm(instance=report)
        report_event_formset = forms.ReportEventFormset(instance=report)
        report_link_formset = forms.ReportLinkFormset(instance=report)

    return render(request, 'edit_report.html',
                  {'report_form': report_form,
                   'report_event_formset': report_event_formset,
                   'report_link_formset': report_link_formset,
                   'pageuser': user,
                   'year': year,
                   'month': month,
                   'created': created})
