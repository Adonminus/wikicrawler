import asyncio
import aiohttp
from bs4 import BeautifulSoup

class Node():
    def __init__(self, data, parent):
        self.data = data
        self.parent = parent
        if(parent is not None):
            self.depth = parent.depth+1
        else:
            self.depth = 0
        self.children = []

    def add_child(self, obj):
        self.children.append(obj)
        
    def print_path(self):
        if(self.parent is None):
            print(self.data, end =" ")
        else:
            self.parent.print_path()
            print( ' --> ' + self.data, end =" ")
        

async def search_path(origin, dest, depth):
    sem = asyncio.Semaphore(300)
    queue = []
    queue.append(Node(origin, None))
    visited = set()
    visited.add(origin)
    found = [False]
    
    while(len(queue) > 0 and not found[0]):
        coros = [
            process_single_page(node, queue, found, visited, dest, depth, sem)
            for node
            in queue
        ]
        await asyncio.gather(*coros)

async def get(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.text()
            
async def process_single_page(snode, queue, found, visited, dest, depth, sem):
    async with sem:
        response = await get('https://en.wikipedia.org/wiki/' + snode.data)
        soup = BeautifulSoup(response, 'lxml')
        aTags = soup.find(id="mw-content-text").find_all('a', href=True)
        result = []

        for aTag in aTags:
            if(aTag.get('href').startswith('/wiki/') and not ':' in aTag.get('href')):
                newnode = Node(aTag.get('href').replace('/wiki/', ''), snode)
                result.append(newnode)
        for node in result:
            if(found[0]): break
            if(node.depth >= depth): break
            if(not node.data in visited):
                print(str(node.depth) + '. ' + ' ' + node.data)
                queue.append(node)
                visited.add(node.data)
            if(node.data == dest):
                found[0] = True
                print('')
                node.print_path()
                break
        queue.remove(snode)
        return

async def main():
    origin = input("Enter origin page name: ") 
    dest = input("Enter destination page name: ") 
    maxDepth = input("Enter max search depth: ")
    print('Searching path from ' + origin + ' to ' + dest)
    await search_path(origin, dest, int(maxDepth))


loop = asyncio.ProactorEventLoop()
asyncio.set_event_loop(loop)
asyncio.run(main())
