from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import Q
from datetime import datetime 

from .models import Mobil, Pesanan, Testimoni
from .forms import FormPesanan, FormTestimoni

def car_list(request):

    q = request.GET.get('sort')
    q2 = request.GET.get('filter')
    mobil_all = Mobil.objects.all()

    sort_murah = mobil_all.order_by('harga')
    sort_mahal = mobil_all.order_by('-harga')
    relevance = mobil_all.order_by("-ditambahkan")

    if request.method == "POST":
        kategori = request.POST.getlist('kategori')
        transmisi = request.POST.getlist('transmisi')

        if kategori and transmisi:
            for i in kategori: 
                for j in transmisi:
                    if len(kategori) > 1:
                        filtered = mobil_all.filter(Q(tipe__in=kategori) & Q(transmisi__in=transmisi))
                    elif len(kategori) == 1 and len(transmisi) > 1:
                        filtered = mobil_all.filter(Q(tipe=i) & Q(transmisi__in=transmisi))

                    else:
                        filtered = mobil_all.filter(Q(tipe__in=kategori) & Q(transmisi=j))

        elif kategori:
            for i in kategori:
                filtered = mobil_all.filter(Q(tipe=i))

        elif transmisi:
            for i in transmisi:
                filtered = mobil_all.filter(transmisi__in=transmisi)
        else:
            filtered = mobil_all


        sort_murah = filtered.order_by('harga')
        sort_mahal = filtered.order_by('-harga')
        relevance = filtered.order_by('-ditambahkan')

        context = {
                'mobil_all':mobil_all,
                'murah':sort_murah,
                'mahal':sort_mahal,
                'q':q,
                'filtered':filtered,
                'relevance':relevance,
        }

    else:

        context = {
                'mobil_all':mobil_all,
                'murah':sort_murah,
                'mahal':sort_mahal,
                'q':q,
                'relevance':relevance,
        }

    return render(request, 'sewa_mobil/car.html', context)

@login_required
def pesanan_view(request):

    q = request.GET.get('car')
    terpesan = False

    if request.method == 'POST':
        form_pesan = FormPesanan(request.POST, request.FILES)

        if form_pesan.is_valid():
            status = form_pesan.cleaned_data['mobil']
            mobil = Mobil.objects.get(id=status.id)

            if mobil.status == "Not Available":
                return HttpResponse("Mobil tidak Tersedia")
            else:
                terpesan = True
                mobil.status = 'Not Available'
                mobil.save()
                pesanan = form_pesan.save()

            return HttpResponseRedirect(reverse('dashboard'))
        else:
            print(form_pesan.errors)
    else:
        if q:
            form_pesan = FormPesanan(initial={'mobil':Mobil.objects.get(plat=q)})
        else:
            form_pesan = FormPesanan()

    return render(request, 'sewa_mobil/form_pemesanan.html', {'form':form_pesan, 'terpesan':terpesan})

@login_required
def detail_view(request, slug):
    model = get_object_or_404(Mobil, slug=slug)
    testimoni_baru = None
    testimoni_ = Testimoni.objects.filter(mobil__id=model.id)
    
    if request.method == "POST":
        testimoni = FormTestimoni(data=request.POST)
        if testimoni.is_valid():
            testimoni_baru = testimoni.save(commit=False)
            testimoni_baru.mobil = model
            testimoni_baru.save()
            testimoni = FormTestimoni()
        else:
            return HttpResponse("Mohon Ulangi")
    else:
        testimoni = FormTestimoni()

    return render(request, 'sewa_mobil/product-detail.html', {'mobil':model, 'testi':testimoni, 'testi_baru':testimoni_baru, 'testimoni':testimoni_})

def batal_pesan(request):
    
    q = request.GET.get("plat")

    if request.method == 'POST':
        if q:
            pesanan = get_object_or_404(Pesanan, mobil__plat=q)
            if request.user == pesanan.user:
                mobil = get_object_or_404(Mobil, plat=q)
                mobil.status = "Available"
                mobil.save()
                pesanan.delete()
            else:
                return HttpResponseForbidden()
        else:
            HttpResponseForbidden()

    return render(request, 'sewa_mobil/batal_pesan.html')
 
