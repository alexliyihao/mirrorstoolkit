def from_tensor(x):
    """
    the reverse operation of torchvision.transforms.ToTensor
    Converts a PIL Image or numpy.ndarray (H x W x C) in the range [0, 255]
    to a torch.FloatTensor of shape (C x H x W) in the range [0.0, 1.0]
    """
    x = x.detach()
    x = x.permute((1,2,0)) * 255
    return x.cpu().numpy()

#When working with [-1,1] tensor rather than [0,1]
def norm(x):
    """convert [0,1] to [-1,1] scale"""
    out = (x -0.5) *2
    return out.clamp(-1, 1)

def denorm(x):
    """convert [-1,1] to [0,1] scale"""
    out = (x + 1) / 2
    return out.clamp(0, 1)

def np_to_tensor(x):
    """convert [0,255] h*w*c np.array to [-1,1] s*c*h*w tensor"""
    x = x[:,:,:,None].transpose((3, 2, 0, 1))/255
    x = torch.from_numpy(x).to(torch.device('cuda'))
    x = x.type(torch.cuda.FloatTensor)
    x = norm(x)
    return x

def tensor_to_np(x):
    """convert [-1,1] s*c*h*w tensor to [0,255] np.array form, never used, just in case needed"""
    x = x[0]
    x = x.permute((1,2,0))
    x = 255*denorm(x)
    x = x.cpu().numpy()
    x = x.astype(np.uint8)
    return x

def tensor_to_np_format_tensor(x):
    """convert a [-1,1] s*c*w*h tensor to a [0,255] w*h*c tensor"""
    x = denorm(x[0].permute((1,2,0)))*255
    return x

def np_format_tensor_to_tensor(x):
    """convert a [0,255] w*h*c tensor to a [-1,1] s*c*w*h tensor"""
    x = x[:,:,:,None].permute(3, 2, 0, 1)/255
    return norm(x)
