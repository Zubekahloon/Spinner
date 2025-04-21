
from django.shortcuts import render, redirect, HttpResponse
from .models import User, AssignedHouse, House
from django.contrib import messages
import os, csv
from django.http import JsonResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage 



def index(request):
    return render(request, "index.html")

def add_user(request):
    if request.method == "POST":
        name = request.POST.get("name")
        territory = request.POST.get("territory")

        if name and territory:
            user, created = User.objects.get_or_create(territory=territory, defaults={"name": name})
            if created:
                messages.success(request, "User added successfully!")
            else:
                messages.warning(request, "User with this territory already exists!")
        else:
            messages.error(request, "All fields are required!")

        return redirect("display_users")

    return render(request, "user/add_user.html")


def display_users(request):
    users = User.objects.all()
    return render(request, "user/display_users.html", {"users": users})


def deluser(request,id):
    try:
        dele = User.objects.get(id=id)
        dele.delete()

    except User.DoesNotExist:
        pass

    return redirect('display_users')


def updateuser(request,id):
    try:
       myuser = User.objects.get(id=id)
       return render(request, 'user/updateuser.html', {'myuser': myuser})
    
    except User.DoesNotExist:
        return redirect('display_users')


def do_updateuser(request, id):
    user = User.objects.get(id=id)
    if request.method == "POST":
        new_name = request.POST.get("name")
        new_territory = request.POST.get("territory")


        if User.objects.filter(territory=new_territory).exclude(id=user.id).exists():
            messages.error(request, f"The email {new_territory} is already in use by another user.")
        else:
            user.name = new_name
            user.territory = new_territory

            user.save()
            messages.success(request, "User information updated successfully!")

        return redirect('display_users')

    return render(request, 'user/updateuser.html', {'myuser': user})



def assign_house_to_user(request, house_csv_file, house_number):
    try:
        house_list_path = os.path.join(settings.MEDIA_ROOT, "upload_houses_no", house_csv_file)
        assigned_houses_path = os.path.join(settings.MEDIA_ROOT, "data/assigned_house_to_user.csv")

        assigned_house = AssignedHouse.objects.filter(house_number=house_number).select_related('user').first()
        if not assigned_house:
            return JsonResponse({"success": False, "message": "Plot Not Found!"}, status=400)

        user = assigned_house.user  

        if os.path.exists(assigned_houses_path):
            with open(assigned_houses_path, "r", newline="") as file:
                reader = csv.reader(file)
                for row in reader:
                    if str(house_number) in row:
                        return JsonResponse({"success": False, "message": f"Plot No {house_number} is already recorded!"}, status=400)


        os.makedirs(os.path.dirname(assigned_houses_path), exist_ok=True)
        with open(assigned_houses_path, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([user.name, user.territory, house_number])

       
        if os.path.exists(house_list_path):
            with open(house_list_path, "r", newline="") as file:
                houses = list(csv.reader(file))

            updated_houses = [row for row in houses if row and row[0] != str(house_number)]

            with open(house_list_path, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerows(updated_houses)

        return JsonResponse({
            "success": True,
            "user_name": user.name,
            "territory": user.territory,
            "house_number": house_number
        })

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)


def assign_house(request):
    error = ""
    
    if request.method == "POST":
        user_id = request.POST.get("user")
        house_number = request.POST.get("house_number")

        if not user_id or not house_number:
            error = "Please fill all fields!"

        else:
            user = User.objects.get(id=user_id)
        
            if AssignedHouse.objects.filter(house_number=house_number).exists():
                error = f"Plot No {house_number} is already assigned!"
            else:
                AssignedHouse.objects.create(user=user, house_number=house_number)
                return redirect("assign_house") 

    users = User.objects.all()
    return render(request, "assignhouse/assign_house.html", {"users": users, "error": error})


def assign_house_display(request):
    assigned_houses = AssignedHouse.objects.select_related("user").all() 
    return render(request, "assignhouse/display_assigned_houses.html", {"assigned_houses": assigned_houses})


def delassignhouse(request,id):
    try:
        assigned_house = AssignedHouse.objects.get(id=id)
        assigned_house.delete()
    except AssignedHouse.DoesNotExist:
        pass

    return redirect('assign_house_display')


def updateassignhouse(request,id):
    try:
        assigned_house = AssignedHouse.objects.get(id=id)
        users = User.objects.all()  
        return render(request, 'assignhouse/updateassignhouse.html', {'assigned_house': assigned_house, 'users': users})
    
    except AssignedHouse.DoesNotExist:
        return redirect('assign_house_display')
    

def do_updateassignhouse(request, id):
    try:
        assigned_house = AssignedHouse.objects.get(id=id) 
    except AssignedHouse.DoesNotExist:
        return redirect('assign_house_display')

    if request.method == "POST":
        user_id = request.POST.get("user")
        house_number = request.POST.get("house_number")

        if user_id and house_number:
           
            if AssignedHouse.objects.filter(house_number=house_number).exclude(id=id).exists():
                messages.error(request, f"Plot {house_number} is already assigned to another user!")
            else:
                assigned_house.user = User.objects.get(id=user_id)
                assigned_house.house_number = house_number
                assigned_house.save()
                messages.success(request, "Plot updated successfully!")
                return redirect('assign_house_display')

    return redirect('assign_house_display')




def download_assigned_csv(request):
    file_path = os.path.join(settings.MEDIA_ROOT, 'data/assigned_house_to_user.csv')
    
    if not os.path.exists(file_path):
        return HttpResponse("No file found.", status=404)

    with open(file_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="assigned_house_to_user.csv"'
        return response


def clear_assigned_csv(request):
    file_path = os.path.join(settings.MEDIA_ROOT, 'data/assigned_house_to_user.csv')

    if os.path.exists(file_path):
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Name', 'Territory', 'Plot Number'])
        
        return redirect('index')
    
    return HttpResponse("File not found.", status=404)





def adminpanel(request):
    total_user = User.objects.all().count()
    total_AssignedHouse = AssignedHouse.objects.all().count()
    total_house = House.objects.all().count()

    total_user_list=[]

    tusers = User.objects.all()
    for tuser in tusers:
        
        tuserz = User.objects.filter(id=tuser.id).count()
        total_user_list.append(tuserz)


    total_AssignedHouse_list=[]
    tahs = AssignedHouse.objects.all()
    for tah in tahs:
        
        tahz = AssignedHouse.objects.filter(id=tah.id).count()
        total_AssignedHouse_list.append(tahz)
    

    context = {
            'page_title': "Administrative Dashboard",
            'total_user': total_user,
            'total_house': total_house,
            'total_AssignedHouse': total_AssignedHouse,
            'total_user_list': total_user_list,
            'total_AssignedHouse_list': total_AssignedHouse_list,
            }
    return render(request, 'main_admin/home_admin.html', context)


def upload_csv(request):
    if request.method == "POST" and request.FILES.get("csv_file"):
        csv_file = request.FILES["csv_file"]
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, "upload_assigned_houses"))
         
        upload_path = os.path.join(fs.location, "assigned_houses_upload.csv")
        if os.path.exists(upload_path):
            os.remove(upload_path)

        filename = fs.save("assigned_houses_upload.csv", csv_file)
        file_path = fs.path(filename)

        with open(file_path, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader) 

            for row in reader:
                if len(row) < 4:
                    print("Skipping row due to insufficient data:", row)
                    continue

                serialno = row[0].strip()
                name = row[1].strip()
                territory_raw = row[2].strip().replace("\n", " ").replace("\r", " ")
                house_number = row[3].strip()

                if AssignedHouse.objects.filter(house_number=house_number).exists():
                    print(f"❌ Plot {house_number} assigning. Skipping...")
                    continue

                user, _ = User.objects.get_or_create(
                    name=name,
                    territory=territory_raw,
                )

                AssignedHouse.objects.create(user=user, house_number=house_number)
                print(f"✅ Assigned Plot {house_number} to {name}")

        return redirect("upload_csv")  

    return render(request, "csv_file_uploaded/upload_csv.html")



def display_uploaded_csv_files(request):
    uploads_dir = os.path.join(settings.MEDIA_ROOT, "upload_assigned_houses")
    
    files = os.listdir(uploads_dir)

    uploaded_files = [file for file in files if os.path.isfile(os.path.join(uploads_dir, file))]
    
    return render(request, "csv_file_uploaded/display_upload_csv_files.html", {"uploaded_files": uploaded_files})


def delete_uploaded_csv_file(request, filename):
    fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, "upload_assigned_houses"))
    file_path = fs.path(filename)

    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)  # skip header
        house_numbers_to_delete = []

        for row in reader:
            # Skip rows with incorrect format
            if len(row) < 4:
                print("Skipping malformed row:", row)
                continue

            serialno = row[0].strip()
            name = row[1].strip()
            territory = row[2].strip()
            house_number = row[3].strip()
            
            house_numbers_to_delete.append(house_number)

        AssignedHouse.objects.filter(house_number__in=house_numbers_to_delete).delete()
        print(f"✅ Deleted AssignedPlot records for Plots: {house_numbers_to_delete}")

    fs.delete(filename)
    print(f"🗑️ Deleted uploaded file: {file_path}")

    return redirect("display_uploaded_csv_files")





def upload_houses_csv(request):
    if request.method == "POST" and request.FILES.get("csv_file"):
        new_filename = "house_csv_file.csv"
        upload_path = os.path.join(settings.MEDIA_ROOT, "upload_houses_no")

        os.makedirs(upload_path, exist_ok=True)

        file_path = os.path.join(upload_path, new_filename)

        if os.path.exists(file_path):
            os.remove(file_path)

        fs = FileSystemStorage(location=upload_path)
        fs.save(new_filename, request.FILES["csv_file"])

        with open(file_path, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            # next(reader) 
            house_numbers = set()

            for row in reader:
                house_number = row[0].strip() if row else ""
                if house_number:
                    if house_number not in house_numbers and not House.objects.filter(house_number=house_number).exists():
                        house_numbers.add(house_number)

        for house_number in house_numbers:
            House.objects.create(house_number=house_number)

        return redirect("upload_houses_csv")

    return render(request, "houses/upload_houses_csv.html")


def display_houses_csv_files(request):
    uploads_dir = os.path.join(settings.MEDIA_ROOT, "upload_houses_no")
    files = os.listdir(uploads_dir)

    display_files = [file for file in files if os.path.isfile(os.path.join(uploads_dir, file))]

    total_houses_from_csv = 0
    for file in display_files:
        file_path = os.path.join(uploads_dir, file)

        with open(file_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
            total_houses_from_csv += len(lines)

    return render(request, "houses/display_houses_csv.html", {"display_files": display_files, "total_houses": total_houses_from_csv})


def delete_houses_csv(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, 'upload_houses_no', filename)

    if os.path.exists(file_path):
        os.remove(file_path)

        House.objects.all().delete()

        message = f"File '{filename}' deleted successfully, and all plot records removed from the database."
    else:
        message = f"File '{filename}' not found."

    messages.success(request, message)
    return redirect("display_houses_csv_files")




def participated(request):
    participaant = AssignedHouse.objects.select_related("user").all() 
    return render(request, "participant.html", {"participaant": participaant})
