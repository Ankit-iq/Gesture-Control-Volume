#Problem Statement: Create a linked list with four nodes linking with each other
class Node:
    def __init__(self,val:float):
        self.data=val
        self.next=None

#Creating four nodes
node1= Node(1.0)
node2= Node(2)
node3= Node(3.7)
node4= Node(4.1)

#linking nodes
node1.next=node2
node2.next=node3
node3.next=node4

#function to print the whole linked list
def print_linked_list(head):
    current_node=head
    while current_node is not None:
        print(current_node.data)
        current_node=current_node.next

print_linked_list(node1) #call the function and pass the head node param


