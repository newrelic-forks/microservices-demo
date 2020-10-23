using System;
using System.Diagnostics;

namespace cartservice
{

    internal static class CartActivity
    {
        public static readonly ActivitySource ActivitySource = new ActivitySource("cartservice");

        public const string ActivityName = "cartservice";
    }
    
}
