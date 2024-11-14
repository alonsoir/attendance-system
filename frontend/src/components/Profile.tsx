import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

const Profile: React.FC = () => {
 const [isEditing, setIsEditing] = React.useState(false);
 const [user] = React.useState({
   name: 'John Doe',
   email: 'john@example.com',
   role: 'Teacher',
   department: 'Computer Science'
 });

 return (
   <div className="container mx-auto p-4">
     <Card>
       <CardHeader>
         <CardTitle>Profile</CardTitle>
       </CardHeader>
       <CardContent>
         <div className="space-y-4">
           <div>
             <label className="font-bold">Name:</label>
             <p>{user.name}</p>
           </div>
           <div>
             <label className="font-bold">Email:</label>
             <p>{user.email}</p>
           </div>
           <div>
             <label className="font-bold">Role:</label>
             <p>{user.role}</p>
           </div>
           <div>
             <label className="font-bold">Department:</label>
             <p>{user.department}</p>
           </div>

           <Button onClick={() => setIsEditing(!isEditing)}>
             {isEditing ? 'Cancel' : 'Edit Profile'}
           </Button>
         </div>
       </CardContent>
     </Card>
   </div>
 );
};

export default Profile;